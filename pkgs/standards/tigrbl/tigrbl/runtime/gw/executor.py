from __future__ import annotations

import json
import inspect
from types import SimpleNamespace
from typing import Any

from ..._concrete._request import Request
from ..._concrete.dependencies import Dependency
from ...mapping import engine_resolver as _resolver
from ..status.exceptions import StatusDetailError
from .. import events as _events
from ..atoms.deps_inject.runtime import invoke_dependency as _invoke_dependency
from ..executor import _Ctx, _invoke
from ..kernel.core import Kernel
from ..kernel.atoms import _discover_atoms
from .raw import GwRawEnvelope


class RawEnvelopeExecutor:
    """Runtime ingress for ASGI3 raw envelopes."""

    def __init__(self, *, app: Any) -> None:
        self.app = app
        self._kernel = Kernel()
        self._route_atoms: list[tuple[str, Any]] | None = None

    def _routing_atoms(self) -> list[tuple[str, Any]]:
        if self._route_atoms is not None:
            return self._route_atoms
        order = {name: idx for idx, name in enumerate(_events.all_events_ordered())}
        atoms = []
        for anchor, run in _discover_atoms():
            if _events.phase_for_event(anchor) not in {
                "INGRESS_BEGIN",
                "INGRESS_PARSE",
                "INGRESS_ROUTE",
            }:
                continue
            atoms.append((anchor, run))
        atoms.sort(key=lambda item: order.get(item[0], 10_000))
        self._route_atoms = atoms
        return atoms

    async def invoke(self, env: GwRawEnvelope) -> None:
        scope_type = env.scope.get("type")

        if scope_type == "lifespan":
            await self._handle_lifespan(env)
            return

        if scope_type != "http":
            return

        await self._invoke_http(env)

    async def _invoke_http(self, env: GwRawEnvelope) -> None:
        plan = self._kernel.kernel_plan(self.app)
        ctx = _Ctx.ensure(request=None, db=None)
        ctx.app = self.app
        ctx.router = self.app
        ctx.raw = env
        ctx.kernel_plan = plan

        for _anchor, atom_run in self._routing_atoms():
            result = atom_run(None, ctx)
            if hasattr(result, "__await__"):
                await result

        route = ctx.temp.get("route", {}) if isinstance(ctx.temp, dict) else {}
        request = self._build_request(env, route, ctx)
        opmeta_index = route.get("opmeta_index")
        if not isinstance(opmeta_index, int) or not (
            0 <= opmeta_index < len(plan.opmeta)
        ):
            if await self._try_dispatch_non_runtime_route(env, request):
                return
            await self._send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        opmeta = plan.opmeta[opmeta_index]
        ctx.model = opmeta.model
        ctx.op = opmeta.alias
        ctx.opview = self._kernel.get_opview(self.app, opmeta.model, opmeta.alias)
        ctx.request = request
        ctx.payload = route.get("payload")
        ctx.path_params = route.get("path_params") or {}
        if isinstance(ctx.path_params, dict):
            request.path_params = dict(ctx.path_params)
            request.scope["path_params"] = dict(ctx.path_params)

        db = None
        release_db = None
        try:
            db, release_db = _resolver.acquire(
                router=self.app, model=opmeta.model, op_alias=opmeta.alias
            )
        except Exception:
            db = None
            release_db = None
            model_engine = getattr(opmeta.model, "engine", None)
            app_engine = getattr(self.app, "engine", None)
            try:
                if model_engine is not None:
                    _resolver.register_table(opmeta.model, model_engine)
                if app_engine is not None:
                    _resolver.set_default(app_engine)
                    if opmeta.model is not None:
                        _resolver.register_table(opmeta.model, app_engine)
                db, release_db = _resolver.acquire(
                    router=self.app, model=opmeta.model, op_alias=opmeta.alias
                )
            except Exception:
                db = None
                release_db = None
        if db is None:
            db, release_db = await self._acquire_model_db(opmeta.model, request)
        ctx.db = db

        selected = dict(plan.phase_chains.get(opmeta_index, {}))
        selected["INGRESS_BEGIN"] = []
        selected["INGRESS_PARSE"] = []
        selected["INGRESS_ROUTE"] = []

        invoke_error: Exception | None = None
        try:
            await _invoke(request=request, db=db, phases=selected, ctx=ctx)
        except Exception as exc:  # convert runtime exceptions into transport responses
            invoke_error = exc
        finally:
            if release_db is not None:
                try:
                    maybe = release_db()
                    if inspect.isawaitable(maybe):
                        await maybe
                except Exception:
                    pass

        if invoke_error is not None:
            if isinstance(invoke_error, StatusDetailError):
                await self._send_json(
                    env,
                    int(getattr(invoke_error, "status_code", 500) or 500),
                    {"detail": getattr(invoke_error, "detail", str(invoke_error))},
                )
                return
            await self._send_json(
                env,
                500,
                {"detail": str(invoke_error)},
            )
            return

        egress = ctx.temp.get("egress", {}) if isinstance(ctx.temp, dict) else {}
        response = (
            egress.get("transport_response") if isinstance(egress, dict) else None
        )
        if isinstance(response, dict):
            if int(response.get("status_code", 200) or 200) == 200 and getattr(
                opmeta, "target", None
            ) in {"create", "bulk_create"}:
                response["status_code"] = 201
            await self._send_transport_response(env, response)
            return

        status = int(getattr(ctx, "status_code", 200) or 200)
        body = getattr(ctx, "result", None)
        await self._send_json(env, status, body)

    async def _acquire_model_db(self, model: Any, request: Any) -> tuple[Any, Any]:
        if model is None:
            return None, None
        get_db = getattr(model, "__tigrbl_get_db__", None)
        if not callable(get_db):
            return None, None
        try:
            out = get_db(request)
        except TypeError:
            out = get_db()

        if inspect.isgenerator(out):
            gen = out
            try:
                value = next(gen)
            except StopIteration:
                value = None
            return value, gen.close

        if inspect.isasyncgen(out):
            agen = out
            try:
                value = await anext(agen)
            except StopAsyncIteration:
                value = None
            return value, agen.aclose

        if inspect.isawaitable(out):
            return await out, None

        return out, None

    def _build_request(
        self, env: GwRawEnvelope, route: dict[str, Any], ctx: Any
    ) -> Any:
        scope = dict(env.scope)
        path_params = route.get("path_params")
        if isinstance(path_params, dict):
            scope["path_params"] = path_params
        request = Request(scope, app=self.app, state=SimpleNamespace())
        body = getattr(ctx, "body", None)
        if isinstance(body, (bytes, bytearray)):
            request.body = bytes(body)
        return request

    async def _try_dispatch_non_runtime_route(
        self, env: GwRawEnvelope, request: Any
    ) -> bool:
        method = str(env.scope.get("method", "GET")).upper()
        path = str(env.scope.get("path", "/"))
        for route in getattr(self.app, "routes", ()) or ():
            methods = getattr(route, "methods", ()) or ()
            if method not in methods:
                continue
            pattern = getattr(route, "pattern", None)
            if pattern is None:
                continue
            matched = pattern.match(path)
            if matched is None:
                continue

            request.path_params = dict(matched.groupdict())
            request.scope["path_params"] = request.path_params
            handler = getattr(route, "handler", None) or getattr(
                route, "endpoint", None
            )
            if not callable(handler):
                continue
            response = await self._invoke_handler(handler, request)
            if all(
                hasattr(response, attr) for attr in ("status_code", "headers", "body")
            ):
                await self._send_transport_response(
                    env,
                    {
                        "status_code": int(
                            getattr(response, "status_code", 200) or 200
                        ),
                        "headers": {
                            str(k): str(v)
                            for k, v in (getattr(response, "headers", {}) or {}).items()
                        },
                        "body": getattr(response, "body", b""),
                    },
                )
            elif isinstance(response, dict) and any(
                key in response
                for key in (
                    "status_code",
                    "headers",
                    "raw_headers",
                    "body_iterator",
                    "media_type",
                    "path",
                    "url",
                )
            ):
                await self._send_transport_response(env, response)
            elif (
                isinstance(response, dict)
                and "body" in response
                and len(response) == 1
                and isinstance(response.get("body"), (str, bytes, bytearray))
            ):
                await self._send_transport_response(env, response)
            else:
                await self._send_json(env, 200, response)
            return True
        return False

    async def _invoke_handler(self, handler: Any, request: Any) -> Any:
        sig = inspect.signature(handler)
        kwargs: dict[str, Any] = {}
        for name, param in sig.parameters.items():
            if name == "request":
                kwargs[name] = request
            elif name in request.path_params:
                kwargs[name] = request.path_params[name]
            elif isinstance(param.default, Dependency):
                kwargs[name] = await _invoke_dependency(
                    self.app, param.default.dependency, request
                )
            elif param.default is inspect._empty:
                kwargs[name] = request
        result = handler(**kwargs) if kwargs else handler()
        if hasattr(result, "__await__"):
            return await result
        return result

    async def _send_transport_response(
        self, env: GwRawEnvelope, response: dict[str, Any]
    ) -> None:
        status = int(response.get("status_code", 200) or 200)
        headers_obj = response.get("headers")
        headers: list[tuple[bytes, bytes]] = []
        if isinstance(headers_obj, dict):
            headers = [
                (str(k).encode("latin-1"), str(v).encode("latin-1"))
                for k, v in headers_obj.items()
            ]
        raw_headers = response.get("raw_headers")
        if isinstance(raw_headers, (list, tuple)):
            headers.extend(
                [
                    (bytes(k), bytes(v))
                    for k, v in raw_headers
                    if isinstance(k, (bytes, bytearray))
                    and isinstance(v, (bytes, bytearray))
                ]
            )
        body = response.get("body", b"")
        while isinstance(body, dict) and "body" in body and len(body) == 1:
            body = body.get("body")
        if isinstance(body, str):
            try:
                from pathlib import Path

                candidate = Path(body)
                if candidate.exists() and candidate.is_file():
                    body = candidate.read_bytes()
            except Exception:
                pass
        if (body is None or body == b"" or body == "") and isinstance(
            response.get("path"), str
        ):
            try:
                from pathlib import Path

                body = Path(response["path"]).read_bytes()
            except Exception:
                body = b""
        body_iter = response.get("body_iterator")
        if (body is None or body == b"" or body == "") and body_iter is not None:
            chunks: list[bytes] = []
            if hasattr(body_iter, "__aiter__"):
                async for chunk in body_iter:
                    if isinstance(chunk, (bytes, bytearray)):
                        chunks.append(bytes(chunk))
                    elif isinstance(chunk, str):
                        chunks.append(chunk.encode("utf-8"))
            body = b"".join(chunks)
        if isinstance(body, str):
            body = body.encode("utf-8")
        elif body is None:
            body = b""
        elif not isinstance(body, (bytes, bytearray)):
            body = json.dumps(self._json_safe(body)).encode("utf-8")

        await env.send(
            {"type": "http.response.start", "status": status, "headers": headers}
        )
        await env.send(
            {"type": "http.response.body", "body": bytes(body), "more_body": False}
        )

    async def _send_json(self, env: GwRawEnvelope, status: int, payload: Any) -> None:
        await env.send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await env.send(
            {
                "type": "http.response.body",
                "body": json.dumps(self._json_safe(payload)).encode("utf-8"),
                "more_body": False,
            }
        )

    def _json_safe(self, payload: Any) -> Any:
        seen: set[int] = set()

        def _walk(value: Any) -> Any:
            if value is None or isinstance(value, (bool, int, float, str)):
                return value
            if isinstance(value, bytes):
                return value.decode("utf-8", errors="replace")
            if isinstance(value, bytearray):
                return bytes(value).decode("utf-8", errors="replace")
            if isinstance(value, dict):
                oid = id(value)
                if oid in seen:
                    return None
                seen.add(oid)
                return {str(k): _walk(v) for k, v in value.items()}
            if isinstance(value, (list, tuple, set)):
                oid = id(value)
                if oid in seen:
                    return []
                seen.add(oid)
                return [_walk(v) for v in value]
            if hasattr(value, "__dict__"):
                oid = id(value)
                if oid in seen:
                    return None
                seen.add(oid)
                return {
                    k: _walk(v)
                    for k, v in vars(value).items()
                    if not str(k).startswith("_")
                }
            return str(value)

        return _walk(payload)

    async def _handle_lifespan(self, env: GwRawEnvelope) -> None:
        while True:
            message = await env.receive()
            message_type = message.get("type")
            if message_type == "lifespan.startup":
                await self.app.run_event_handlers("startup")
                await env.send({"type": "lifespan.startup.complete"})
                continue
            if message_type == "lifespan.shutdown":
                await self.app.run_event_handlers("shutdown")
                await env.send({"type": "lifespan.shutdown.complete"})
            return

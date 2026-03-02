from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Mapping, Optional, Union

from .common import RouterLike, _ensure_router_ns
from ...mapping import engine_resolver as _resolver
from ...core.crud.helpers.model import _single_pk_name
from ...mapping.op_resolver import resolve as resolve_ops
from ...runtime.executor import _Ctx, _invoke
from ...runtime.atoms.deps_inject._common import run_deps as _run_deps

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/rpc")


def _fallback_resolution(
    router: RouterLike, model_or_name: Union[type, str], alias: str
) -> SimpleNamespace:
    if isinstance(model_or_name, type):
        model = model_or_name
    else:
        tables = getattr(router, "tables", {}) or {}
        model = tables.get(model_or_name)
    if model is None:
        raise AttributeError(f"Unknown model '{model_or_name}'")

    specs = resolve_ops(model)
    spec = next((sp for sp in specs if sp.alias == alias), None)
    target = spec.target if spec is not None else alias
    return SimpleNamespace(model=model, target=target)


async def rpc_call(
    router: RouterLike,
    model_or_name: Union[type, str],
    method: str,
    payload: Any = None,
    *,
    db: Any | None = None,
    request: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Call a registered RPC method by (model, method) pair.
    `model_or_name` may be a model class or its name.
    """
    logger.debug("rpc_call invoked for model=%s method=%s", model_or_name, method)
    _ensure_router_ns(router)

    resolution = _fallback_resolution(router, model_or_name, method)
    mdl = resolution.model
    logger.debug(
        "Resolved operation model=%s alias=%s target=%s",
        getattr(mdl, "__name__", mdl),
        method,
        resolution.target,
    )

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        logger.debug(
            "RPC method '%s' not found on %s", method, getattr(mdl, "__name__", mdl)
        )
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    # Acquire DB if not explicitly provided (op > model > router > app)
    _release_db = None
    _provided_db = db is not None
    if db is None:
        try:
            logger.debug(
                "Acquiring DB for rpc_call %s.%s", getattr(mdl, "__name__", mdl), method
            )
            db, _release_db = _resolver.acquire(
                router=router, model=mdl, op_alias=method
            )
        except Exception:
            logger.exception(
                "DB acquire failed for rpc_call %s.%s; no default configured?",
                getattr(mdl, "__name__", mdl),
                method,
            )
            raise
    else:
        logger.debug(
            "Using provided DB for rpc_call %s.%s",
            getattr(mdl, "__name__", mdl),
            method,
        )

    # Ensure execution context contains basic runtime metadata. In tests or
    # other direct calls there may be no ``request`` object to supply an app
    # reference, which the runtime uses to resolve the opview. When absent, the
    # kernel falls back to cached specs for the given model and alias.
    ctx_dict: Dict[str, Any] = dict(ctx or {})
    execute_runtime = bool(ctx_dict.pop("_execute_runtime", True))
    # Opportunistically derive path params from the payload when the caller
    # supplies the primary key in the body. Many RPC handlers expect the
    # identifier via ``ctx['path_params']`` (mirroring REST semantics), but
    # test code invokes ``rpc_call`` directly with the id embedded in the
    # payload.  Normalizing here preserves backwards compatibility and keeps
    # default CRUD handlers happy.
    if isinstance(payload, Mapping):
        try:
            pk_name = _single_pk_name(mdl)
        except Exception:  # model may not be bound to a table
            pk_name = None
        if pk_name and pk_name in payload:
            pp = dict(ctx_dict.get("path_params", {}))
            pp.setdefault(pk_name, payload[pk_name])
            ctx_dict["path_params"] = pp

    try:
        logger.debug("Executing rpc_call %s.%s", getattr(mdl, "__name__", mdl), method)
        result = await fn(payload, db=db, request=request, ctx=ctx_dict)
        if not isinstance(result, Mapping):
            return result

        phases = result.get("phases")
        model = result.get("model")
        alias = result.get("alias")
        if not (isinstance(phases, Mapping) and isinstance(model, type) and alias):
            return result
        if not execute_runtime:
            return result

        exec_ctx = _Ctx.ensure(
            request=result.get("request"),
            db=result.get("db"),
            seed=dict(result.get("ctx") or {}),
        )
        exec_ctx.model = model
        exec_ctx.op = alias
        exec_ctx.payload = result.get("payload")
        serializer = result.get("serialize")
        if callable(serializer):
            exec_ctx.response_serializer = serializer

        phase_chains = dict(phases)
        pre_tx = list(phase_chains.get("PRE_TX_BEGIN", ()) or [])

        async def _run_secdeps(ctx: Any) -> None:
            await _run_deps(ctx, kind="secdep")

        async def _run_deps_step(ctx: Any) -> None:
            await _run_deps(ctx, kind="dep")

        pre_tx.append(_run_secdeps)
        pre_tx.append(_run_deps_step)
        phase_chains["PRE_TX_BEGIN"] = tuple(pre_tx)

        response = await _invoke(
            request=result.get("request"),
            db=result.get("db"),
            phases=phase_chains,
            ctx=exec_ctx,
        )
        # When callers pass an explicit DB session, preserve historical
        # request-style behavior by committing successful RPC calls.
        if _provided_db:
            commit = getattr(db, "commit", None)
            if callable(commit):
                committed = commit()
                if hasattr(committed, "__await__"):
                    await committed
        return response
    finally:
        if _release_db is not None:
            try:
                _release_db()
                logger.debug(
                    "Released DB for rpc_call %s.%s",
                    getattr(mdl, "__name__", mdl),
                    method,
                )
            except Exception:
                logger.debug(
                    "Non-fatal: error releasing acquired DB session (rpc_call)",
                    exc_info=True,
                )

# tigrbl/v3/runtime/executor/invoke.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, MutableMapping, Optional, Union

from .types import _Ctx, PhaseChains, Request, Session, AsyncSession
from .helpers import _in_tx, _run_chain, _g
from .guards import _install_db_guards, _rollback_if_owned
from ..status import create_standardized_error
from ...config.constants import CTX_SKIP_PERSIST_FLAG

logger = logging.getLogger(__name__)


async def _invoke(
    *,
    request: Optional[Request],
    db: Union[Session, AsyncSession, None],
    phases: Optional[PhaseChains],
    ctx: Optional[MutableMapping[str, Any]] = None,
) -> Any:
    """Execute an operation through explicit phases with strict write policies."""

    ctx = _Ctx.ensure(request=request, db=db, seed=ctx)
    if getattr(ctx, "app", None) is None and getattr(ctx, "router", None) is not None:
        ctx.app = ctx.router
    if getattr(ctx, "op", None) is None and getattr(ctx, "method", None) is not None:
        ctx.op = ctx.method
    env = ctx.get("env")
    op_name = getattr(ctx, "op", None) or ctx.get("op") or ctx.get("method")
    if env is None:
        ctx["env"] = SimpleNamespace(method=op_name)
    elif getattr(env, "method", None) in (None, "", "unknown"):
        try:
            env.method = op_name
        except Exception:
            ctx["env"] = SimpleNamespace(method=op_name)
    if getattr(ctx, "model", None) is None:
        obj = getattr(ctx, "obj", None)
        if obj is not None:
            ctx.model = type(obj)
    skip_persist: bool = bool(ctx.get(CTX_SKIP_PERSIST_FLAG) or ctx.get("skip_persist"))

    existed_tx_before = _in_tx(db) if db is not None else False

    async def _run_phase(
        name: str,
        *,
        allow_flush: bool,
        allow_commit: bool,
        in_tx: bool,
        require_owned_for_commit: bool = True,
        nonfatal: bool = False,
        owns_tx_for_phase: Optional[bool] = None,
    ) -> None:
        chain = _g(phases, name)
        if not chain:
            return

        eff_allow_flush = allow_flush and (not skip_persist)
        eff_allow_commit = allow_commit and (not skip_persist)

        owns_tx_now = bool(owns_tx_for_phase)
        if owns_tx_for_phase is None:
            owns_tx_now = not existed_tx_before

        guard = _install_db_guards(
            db,
            phase=name,
            allow_flush=eff_allow_flush,
            allow_commit=eff_allow_commit,
            require_owned_tx_for_commit=require_owned_for_commit,
            owns_tx=owns_tx_now,
        )

        try:
            await _run_chain(ctx, chain, phase=name)
        except Exception as exc:
            ctx.error = exc
            if in_tx:
                await _rollback_if_owned(db, owns_tx_now, phases=phases, ctx=ctx)
            err_name = f"ON_{name}_ERROR"
            try:
                await _run_chain(
                    ctx, _g(phases, err_name) or _g(phases, "ON_ERROR"), phase=err_name
                )
            except Exception:  # pragma: no cover
                pass
            if nonfatal:
                logger.exception("%s failed (nonfatal): %s", name, exc)
                return
            raise create_standardized_error(exc)
        finally:
            guard.restore()

    await _run_phase(
        "INGRESS_BEGIN", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase(
        "INGRESS_PARSE", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase(
        "INGRESS_ROUTE", allow_flush=False, allow_commit=False, in_tx=False
    )
    await _run_phase("PRE_TX_BEGIN", allow_flush=False, allow_commit=False, in_tx=False)

    if not skip_persist:
        await _run_phase(
            "START_TX",
            allow_flush=False,
            allow_commit=False,
            in_tx=False,
            require_owned_for_commit=True,
        )

    await _run_phase(
        "PRE_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "POST_HANDLER", allow_flush=True, allow_commit=False, in_tx=not skip_persist
    )

    await _run_phase(
        "PRE_COMMIT", allow_flush=False, allow_commit=False, in_tx=not skip_persist
    )

    if not skip_persist:
        owns_tx_for_commit = (not existed_tx_before) and (db is not None and _in_tx(db))
        await _run_phase(
            "END_TX",
            allow_flush=True,
            allow_commit=True,
            in_tx=True,
            require_owned_for_commit=True,
            owns_tx_for_phase=owns_tx_for_commit,
        )

    from types import SimpleNamespace as _NS

    serializer = ctx.get("response_serializer")
    if callable(serializer):
        try:
            ctx["result"] = serializer(ctx.get("result"))
        except Exception:
            logger.exception("response serialization failed", exc_info=True)
    else:
        # Compatibility: POST_RESPONSE hooks historically mutate mapping-like
        # payloads (ctx["response"].result["k"] = v). Normalize ORM results so
        # hooks can safely mutate response bodies before transport rendering.
        try:
            result_obj = ctx.get("result")
            is_transport_response = result_obj is not None and all(
                hasattr(result_obj, attr) for attr in ("status_code", "headers", "body")
            )
            if not is_transport_response:
                from ...mapping.rest.helpers import _ensure_jsonable

                ctx["result"] = _ensure_jsonable(result_obj)
        except Exception:
            pass
    temp = ctx.get("temp")
    if isinstance(ctx.get("result"), dict):
        result_map = dict(ctx["result"])
        if isinstance(temp, dict):
            extras = temp.get("response_extras")
            if isinstance(extras, dict):
                for key, value in extras.items():
                    result_map.setdefault(key, value)
        # Keep nullable out fields visible for callers that assert key presence.
        try:
            from ...mapping.column_mro_collect import mro_collect_columns

            model = getattr(ctx, "model", None) or ctx.get("model")
            alias = getattr(ctx, "op", None) or ctx.get("op")
            if isinstance(model, type) and isinstance(alias, str):
                for field, spec in (mro_collect_columns(model) or {}).items():
                    io = getattr(spec, "io", None)
                    out_verbs = tuple(getattr(io, "out_verbs", ()) or ())
                    if alias in out_verbs:
                        result_map.setdefault(field, None)
        except Exception:
            pass
        ctx["result"] = result_map
    ctx.response = _NS(result=ctx.get("result"))

    await _run_phase("POST_COMMIT", allow_flush=True, allow_commit=False, in_tx=False)

    await _run_phase("EGRESS_SHAPE", allow_flush=False, allow_commit=False, in_tx=False)
    await _run_phase(
        "EGRESS_FINALIZE", allow_flush=False, allow_commit=False, in_tx=False
    )

    await _run_phase(
        "POST_RESPONSE",
        allow_flush=False,
        allow_commit=False,
        in_tx=False,
        nonfatal=True,
    )
    if isinstance(temp, dict) and "response_payload" in temp:
        ctx["result"] = temp["response_payload"]
        if hasattr(ctx, "response"):
            ctx.response.result = ctx["result"]
    elif hasattr(ctx, "response"):
        ctx["result"] = getattr(ctx.response, "result", ctx.get("result"))
    return ctx.response.result


__all__ = ["_invoke"]

from __future__ import annotations

import logging
import inspect
from typing import Any, Callable, Optional

from ..._concrete._json_response import JSONResponse
from ... import Request
from .utils import maybe_execute

logger = logging.getLogger(__name__)


def build_healthz_endpoint(dep: Optional[Callable[..., Any]]):
    """
    Returns a ASGI endpoint function for /healthz.
    If `dep` is provided, it's used as a dependency to supply `db`.
    Otherwise, we try request.state.db.
    """
    if dep is not None:
        async def _healthz(request: Request | None = None):
            cleanup_sync = None
            cleanup_async = None
            try:
                try:
                    out = dep(request) if request is not None else dep()
                except TypeError:
                    out = dep()
                if inspect.isgenerator(out):
                    gen = out
                    try:
                        db = next(gen)
                    except StopIteration:
                        db = None
                    cleanup_sync = gen.close
                elif inspect.isasyncgen(out):
                    agen = out
                    try:
                        db = await anext(agen)
                    except StopAsyncIteration:
                        db = None
                    cleanup_async = agen.aclose
                elif inspect.isawaitable(out):
                    db = await out
                else:
                    db = out
                if db is None:
                    return {"ok": True}
                await maybe_execute(db, "SELECT 1")
                return {"ok": True}
            except Exception as e:  # pragma: no cover
                logger.exception("/healthz failed")
                return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
            finally:
                if cleanup_sync is not None:
                    cleanup_sync()
                if cleanup_async is not None:
                    await cleanup_async()

        return _healthz

    async def _healthz(request: Request):
        db = getattr(request.state, "db", None)
        if db is None:
            return {"ok": True}
        try:
            await maybe_execute(db, "SELECT 1")
            return {"ok": True}
        except Exception as e:  # pragma: no cover
            logger.exception("/healthz failed")
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    return _healthz

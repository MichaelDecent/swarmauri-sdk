from __future__ import annotations

import inspect
import warnings
from types import SimpleNamespace
from typing import Any, Iterable

from sqlalchemy import text


def table_iter(router: Any) -> Iterable[type]:
    tables = getattr(router, "tables", None)
    if isinstance(tables, dict) and tables:
        return tables.values()

    return ()


def model_iter(router: Any) -> Iterable[type]:
    warnings.warn(
        "model_iter is deprecated; use table_iter instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return table_iter(router)


def opspecs(model: type):
    indexed = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    declared_raw = getattr(model, "__tigrbl_ops__", ()) or ()
    if isinstance(declared_raw, dict):
        declared = tuple(declared_raw.values())
    else:
        declared = tuple(declared_raw)

    normalized_declared = []
    for sp in declared:
        if hasattr(sp, "alias"):
            normalized_declared.append(sp)
            continue
        if isinstance(sp, dict):
            normalized_declared.append(SimpleNamespace(**sp))
    declared = tuple(normalized_declared)
    if not indexed:
        return declared
    if not declared:
        return indexed

    # Prefer explicitly declared opspecs (decorator/manual assignments), then
    # keep any remaining indexed/default entries for compatibility.
    merged = []
    seen: set[tuple[Any, Any]] = set()
    for sp in declared:
        key = (getattr(sp, "alias", None), getattr(sp, "target", None))
        if key in seen:
            continue
        seen.add(key)
        merged.append(sp)
    for sp in indexed:
        key = (getattr(sp, "alias", None), getattr(sp, "target", None))
        if key in seen:
            continue
        seen.add(key)
        merged.append(sp)
    return tuple(merged)


def label_callable(fn: Any) -> str:
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


def label_hook(fn: Any, phase: str) -> str:
    label = getattr(fn, "__tigrbl_label", None)
    if isinstance(label, str):
        return label
    subj = label_callable(fn).replace(".", ":")
    return f"hook:wire:{subj}@{phase}"


async def maybe_execute(db: Any, stmt: str):
    try:
        rv = db.execute(text(stmt))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
    except Exception:
        rv = db.execute(text("select 1"))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv

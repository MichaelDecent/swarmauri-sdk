from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .core import Kernel


def build_kernelz_payload(kernel: "Kernel", app: Any):
    from .. import events as _ev
    from ...system.diagnostics.utils import label_callable as _label_callable

    payload: dict[str, dict[str, list[str]]] = {}
    table_iter = getattr(app, "tables", {}) or {}
    models = table_iter.values() if hasattr(table_iter, "values") else ()
    for model in models:
        model_name = getattr(model, "__name__", str(model))
        payload[model_name] = {}
        for sp in getattr(getattr(model, "opspecs", object()), "all", ()) or ():
            alias = getattr(sp, "alias", None)
            if not isinstance(alias, str) or not alias:
                continue
            chains = kernel.build(model, alias)
            ordered: list[str] = []

            for dep in getattr(sp, "secdeps", ()) or ():
                dep_fn = getattr(dep, "dependency", dep)
                ordered.append(
                    f"PRE_TX_BEGIN:hook:dep:security:{_label_callable(dep_fn)}"
                )
            for dep in getattr(sp, "deps", ()) or ():
                dep_fn = getattr(dep, "dependency", dep)
                ordered.append(
                    f"PRE_TX_BEGIN:hook:dep:extra:{_label_callable(dep_fn)}"
                )

            if getattr(sp, "persist", "default") != "skip":
                ordered.append("START_TX:hook:sys:txn:begin@START_TX")

            for phase in _ev.PHASES:
                for step in chains.get(phase, ()) or ():
                    label = getattr(step, "__tigrbl_label", None)
                    if not isinstance(label, str):
                        label = _label_callable(step)
                    if (
                        phase == "HANDLER"
                        and label.startswith("tigrbl.core.crud.ops.")
                    ):
                        label = f"hook:wire:{label.replace('.', ':')}@{phase}"
                    ordered.append(f"{phase}:{label}")

            if getattr(sp, "persist", "default") != "skip":
                insert_at = len(ordered)
                for idx, item in enumerate(ordered):
                    if item.startswith("POST_RESPONSE:"):
                        insert_at = idx
                        break
                ordered.insert(insert_at, "END_TX:hook:sys:txn:commit@END_TX")
            payload[model_name][alias] = ordered
    return payload

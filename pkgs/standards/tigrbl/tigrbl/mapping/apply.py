from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from . import columns as _columns_binding
from . import handlers as _handlers_binding
from . import hooks as _hooks_binding
from . import rest as _rest_binding
from . import rpc as _rpc_binding
from . import schemas as _schemas_binding
from .model_helpers import (
    _drop_old_entries,
    _ensure_model_namespaces,
    _index_specs,
)
from .model_registry import (
    _ensure_op_ctx_attach_hook,
    _ensure_registry_listener,
)
from .context import MappingContext


class _SpecList(list):
    """List-like alias bucket with first-item attribute compatibility."""

    def __getattr__(self, name: str) -> Any:
        if not self:
            raise AttributeError(name)
        return getattr(self[0], name)


def apply(context: MappingContext):
    model = context.model
    _ensure_model_namespaces(model)
    _columns_binding.build_and_attach(model)
    _drop_old_entries(model, keys=context.only_keys)
    setattr(model, "__tigrbl_hooks__", context.merged_hooks)

    _schemas_binding.build_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _hooks_binding.normalize_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _handlers_binding.build_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _rpc_binding.register_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _rest_binding.build_router_and_attach(
        model,
        list(context.visible_specs),
        router=context.router,
        only_keys=context.only_keys,
    )

    all_specs, by_key, by_alias = _index_specs(list(context.all_specs))
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    # Back-compat: allow both direct-attr access (e.g. .arity) and indexed
    # access (e.g. [0]) on alias buckets.
    compat_by_alias = {alias: _SpecList(specs) for alias, specs in by_alias.items()}
    model.opspecs = SimpleNamespace(
        all=all_specs,
        by_key=by_key,
        by_alias=compat_by_alias,
    )
    model.alias_map = dict(context.alias_map)

    _ensure_registry_listener(model)
    _ensure_op_ctx_attach_hook(model)
    setattr(model, "__tigrbl_op_ctx_watch__", True)
    return all_specs


__all__ = ["apply"]

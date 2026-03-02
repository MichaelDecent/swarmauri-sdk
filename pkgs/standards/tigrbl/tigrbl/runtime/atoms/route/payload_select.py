from __future__ import annotations

import json
from typing import Any
from collections.abc import Mapping, Sequence

from ... import events as _ev

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def _coerce_path_params(ctx: Any, path_params: Mapping[str, Any]) -> dict[str, Any]:
    model = getattr(ctx, "model", None)
    coerced = dict(path_params)
    if not isinstance(model, type):
        return coerced
    for key, value in list(coerced.items()):
        col = getattr(model, key, None)
        try:
            coerced[key] = col.type.python_type(value)  # type: ignore[attr-defined]
        except Exception:
            pass
    return coerced


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    payload = getattr(ctx, "payload", None)
    if payload is None:
        ingress = temp.get("ingress") if isinstance(temp.get("ingress"), dict) else {}
        payload = ingress.get("body") if isinstance(ingress, dict) else None
    if isinstance(payload, (bytes, bytearray)):
        try:
            payload = json.loads(bytes(payload).decode("utf-8"))
        except Exception:
            pass
    route = temp.setdefault("route", {})
    path_params = route.get("path_params")
    params = route.get("params")

    # If no request body exists, use normalized route params (query + path)
    # so list/clear and nested routes still receive filtering context.
    if payload is None and isinstance(params, Mapping) and params:
        payload = dict(params)

    # Runtime routing bypasses REST endpoint callables, so nested path params
    # must be merged here for create/update/bulk payloads.
    if isinstance(path_params, Mapping) and path_params:
        parent = _coerce_path_params(ctx, path_params)
        if isinstance(payload, Mapping):
            payload = {**dict(payload), **parent}
        elif isinstance(payload, Sequence) and not isinstance(
            payload, (str, bytes, bytearray)
        ):
            merged = []
            for item in payload:
                if isinstance(item, Mapping):
                    merged.append({**dict(item), **parent})
                else:
                    merged.append(item)
            payload = merged
    if payload is not None:
        route["payload"] = payload


__all__ = ["ANCHOR", "run"]

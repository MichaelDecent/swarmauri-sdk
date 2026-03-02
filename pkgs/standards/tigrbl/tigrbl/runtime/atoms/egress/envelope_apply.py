from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_ENVELOPE_APPLY


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    payload = egress.get("wire_payload")
    envelope_default = getattr(getattr(ctx, "response", None), "envelope_default", None)
    is_transport_response = payload is not None and all(
        hasattr(payload, attr) for attr in ("status_code", "headers", "body")
    )
    if payload is not None and envelope_default is True and not is_transport_response:
        egress["enveloped"] = {"data": payload}


__all__ = ["ANCHOR", "run"]

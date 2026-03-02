from __future__ import annotations

from typing import Any

from ... import events as _ev

ANCHOR = _ev.EGRESS_TO_TRANSPORT_RESPONSE


def run(obj: object | None, ctx: Any) -> None:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    payload = egress.get("enveloped", egress.get("wire_payload"))

    if all(hasattr(payload, attr) for attr in ("status_code", "headers", "body")):
        raw_headers = getattr(payload, "headers", {}) or {}
        if hasattr(raw_headers, "items"):
            headers = {str(k): str(v) for k, v in raw_headers.items()}
        elif isinstance(raw_headers, list):
            headers = {str(k): str(v) for k, v in raw_headers}
        else:
            headers = {}
        response = {
            "status_code": int(getattr(payload, "status_code", 200) or 200),
            "headers": headers,
            "body": getattr(payload, "body", b""),
        }
        if hasattr(payload, "body_iterator"):
            response["body_iterator"] = getattr(payload, "body_iterator")
        if hasattr(payload, "path"):
            response["path"] = getattr(payload, "path")
        if hasattr(payload, "url"):
            response["url"] = getattr(payload, "url")
    else:
        response = {
            "status_code": egress.get("status_code", 200),
            "headers": egress.get("headers", {}),
            "body": payload,
        }
    egress["transport_response"] = response


__all__ = ["ANCHOR", "run"]

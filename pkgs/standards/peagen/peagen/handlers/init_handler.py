"""peagen.handlers.init_handler
------------------------------

Async handler dispatching scaffolding operations.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core.init_core import (
    init_project,
    init_template_set,
    init_doe_spec,
    init_ci,
)
from peagen.models.schemas import Task  # type: ignore


async def init_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    payload = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    op = args.get("operation")

    if op == "project":
        return init_project(
            Path(args.get("path", ".")),
            template_set=args.get("template_set", "default"),
            provider=args.get("provider"),
            with_doe=args.get("with_doe", False),
            with_eval_stub=args.get("with_eval_stub", False),
            force=args.get("force", False),
        )
    if op == "template-set":
        return init_template_set(
            Path(args.get("path", ".")),
            name=args.get("name"),
            org=args.get("org"),
            use_uv=args.get("use_uv", True),
            force=args.get("force", False),
        )
    if op == "doe-spec":
        return init_doe_spec(
            Path(args.get("path", ".")),
            name=args.get("name"),
            org=args.get("org"),
            force=args.get("force", False),
        )
    if op == "ci":
        return init_ci(
            github=args.get("github", True),
            force=args.get("force", False),
        )

    raise ValueError(f"Unknown operation: {op}")

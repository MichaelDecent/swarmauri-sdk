"""Diagnostic endpoint exposing kernel phase plans."""

from __future__ import annotations

from typing import Any

from ...runtime.kernel import _default_kernel as K
from ...runtime.kernel.payload import build_kernelz_payload


def _compat_dep_labels(
    payload: dict[str, dict[str, list[str]]],
) -> dict[str, dict[str, list[str]]]:
    """Apply transport compatibility formatting expected by diagnostics tests."""
    out: dict[str, dict[str, list[str]]] = {}
    for model_name, ops in (payload or {}).items():
        out[model_name] = {}
        for alias, steps in (ops or {}).items():
            adjusted: list[str] = []
            for step in steps or ():
                if isinstance(step, str) and ":" in step:
                    phase, label = step.split(":", 1)
                    if (
                        phase == "PRE_TX_BEGIN"
                        and label.startswith("hook:dep:security:")
                        and ":secdep" not in step
                    ):
                        adjusted.append(f"{step}:secdep")
                        continue
                    if (
                        phase == "PRE_TX_BEGIN"
                        and label.startswith("hook:dep:extra:")
                        and not step.endswith(":dep")
                    ):
                        adjusted.append(f"{step}:dep")
                        continue
                    if (
                        phase not in {"START_TX", "END_TX"}
                        and not label.startswith(("hook:", "atom:"))
                    ):
                        wire = label.replace(".", ":")
                        adjusted.append(f"{phase}:hook:wire:{wire}@{phase}")
                        continue
                adjusted.append(step)
            out[model_name][alias] = adjusted
    return out


def build_kernelz_endpoint(router: Any):
    """Return an async handler that serves the Kernel's cached plan."""

    async def _kernelz():
        K.ensure_primed(router)
        return _compat_dep_labels(build_kernelz_payload(K, router))

    return _kernelz


__all__ = ["build_kernelz_endpoint"]

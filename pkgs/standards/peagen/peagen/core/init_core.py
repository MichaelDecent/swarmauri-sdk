"""
peagen.core.init_core
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from peagen.plugins import registry

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent / "template_scaffold"
PROJECT_SRC = TEMPLATES_ROOT / "project"
DOE_SPEC_SRC = TEMPLATES_ROOT / "doe_spec"
CI_SRC = TEMPLATES_ROOT / "ci"


def _ensure_empty_or_force(dst: Path, force: bool) -> None:
    if dst.exists() and any(dst.iterdir()) and not force:
        raise RuntimeError(f"Directory '{dst}' is not empty. Use --force to overwrite.")
    dst.mkdir(parents=True, exist_ok=True)


def _render_scaffold(
    src_root: Path, dst: Path, context: Dict[str, Any], force: bool
) -> None:
    if not src_root.exists():
        raise FileNotFoundError(src_root)

    _ensure_empty_or_force(dst, force)

    env = Environment(
        loader=FileSystemLoader(str(src_root)),
        autoescape=select_autoescape,
        keep_trailing_newline=True,
    )

    for path in src_root.rglob("*"):
        rel = path.relative_to(src_root)
        rendered_parts = [Template(part).render(**context) for part in rel.parts]
        target = dst.joinpath(*rendered_parts)

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        if path.suffix == ".j2":
            template = env.get_template(rel.as_posix())
            target = target.with_suffix("")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template.render(**context), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def init_project(
    path: Path,
    *,
    template_set: str = "default",
    provider: Optional[str] = None,
    with_doe: bool = False,
    with_eval_stub: bool = False,
    force: bool = False,
) -> Dict[str, Any]:
    context = {
        "PROJECT_ROOT": path.name,
        "template_set": template_set,
        "provider": provider or "",
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "peagen_version": "0.0.0",
    }
    _render_scaffold(PROJECT_SRC, path, context, force)
    return {"created": str(path), "next": "peagen process"}


def init_template_set(
    path: Path,
    *,
    name: Optional[str] = None,
    org: Optional[str] = None,
    use_uv: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    tmpl_mod = registry["template_sets"].get("init-template-set")
    if tmpl_mod is None:
        raise ValueError("Template-set 'init-template-set' not found")
    src_root = Path(list(tmpl_mod.__path__)[0])

    context = {"PROJECT_ROOT": name, "org": org or "org", "use_uv": use_uv}
    _render_scaffold(src_root, path, context, force)
    return {"created": str(path), "next": f"peagen template-sets add {path}"}


def init_doe_spec(
    path: Path,
    *,

    name: Optional[str] = None,
    org: Optional[str] = None,
    force: bool = False,
) -> Dict[str, Any]:
    context = {"spec_name": name or path.name, "org": org or "org", "version": "v1"}
    _render_scaffold(DOE_SPEC_SRC, path, context, force)
    return {
        "created": str(path),
        "next": "peagen experiment --spec ... --template project.yaml",
    }


def init_ci(
    *,
    github: bool = True,
    force: bool = False,
) -> Dict[str, Any]:
    kind = "ci-github" if github else "ci-gitlab"
    dst = Path(".")
    _render_scaffold(CI_SRC / kind, dst, {}, force)
    return {"created": str(dst / kind), "next": "commit CI file"}


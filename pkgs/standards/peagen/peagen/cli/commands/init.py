"""CLI front-end for scaffolding Peagen artefacts."""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.handlers.init_handler import init_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
init_app = typer.Typer(help="Bootstrap Peagen artefacts (project, template-set …)")


# ───────────────────────── helpers ─────────────────────────
def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action="init",
        status=Status.pending,
        payload={"args": args},
    )


# ───────────────────────── project ─────────────────────────
project_app = typer.Typer(help="Create a new Peagen project skeleton.")
init_app.add_typer(project_app, name="project")


@project_app.command("run")
def run_project(
    path: Path = typer.Argument(".", exists=False, dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force"),
):
    args = {
        "operation": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    typer.echo(json.dumps(result, indent=2))


@project_app.command("submit")
def submit_project(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    template_set: str = typer.Option("default", "--template-set"),
    provider: Optional[str] = typer.Option(None, "--provider"),
    with_doe: bool = typer.Option(False, "--with-doe"),
    with_eval_stub: bool = typer.Option(False, "--with-eval-stub"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway", envvar="PEAGEN_GATEWAY_URL"
    ),
):
    args = {
        "operation": "project",
        "path": str(path),
        "template_set": template_set,
        "provider": provider,
        "with_doe": with_doe,
        "with_eval_stub": with_eval_stub,
        "force": force,
    }
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(gateway_url, json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))


# ─────────────────────── template-set ──────────────────────
template_set_app = typer.Typer(help="Create a template-set wheel skeleton.")
init_app.add_typer(template_set_app, name="template-set")


@template_set_app.command("run")
def run_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
):
    args = {
        "operation": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    typer.echo(json.dumps(result, indent=2))

@template_set_app.command("submit")
def submit_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name", help="Template-set ID."),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(DEFAULT_GATEWAY, "--gateway-url"),
):
    logger = Logger(name="init_template_set_submit")
    logger.logger.info("Entering init_template_set submit")
    args: Dict[str, Any] = {
        "kind": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    task = _build_task(args)
    envelope = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    try:
        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted init → taskId={task.id}")
    except Exception as exc:  # noqa: BLE001
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
    logger.logger.info("Exiting init_template_set submit")


# ── doe-spec ────────────────────────────────────────────────────────────────
doe_spec_app = typer.Typer(help="Create a DOE-spec stub.")


@doe_spec_app.command("run")
def run_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
):
    logger = Logger(name="init_doe_spec_run")
    logger.logger.info("Entering init_doe_spec run")
    args: Dict[str, Any] = {
        "kind": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    _summary(path, result["next"])
    logger.logger.info("Exiting init_doe_spec run")

@template_set_app.command("submit")
def submit_template_set(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    use_uv: bool = typer.Option(True, "--uv/--no-uv"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway", envvar="PEAGEN_GATEWAY_URL"
    ),
):
    args = {
        "operation": "template-set",
        "path": str(path),
        "name": name,
        "org": org,
        "use_uv": use_uv,
        "force": force,
    }
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(gateway_url, json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))


# ───────────────────────── doe-spec ────────────────────────
doe_spec_app = typer.Typer(help="Create a DOE-spec stub.")
init_app.add_typer(doe_spec_app, name="doe-spec")


@doe_spec_app.command("run")
def run_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
):
    args = {
        "operation": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    typer.echo(json.dumps(result, indent=2))
    
@doe_spec_app.command("submit")
def submit_doe_spec(
    path: Path = typer.Argument(".", dir_okay=True, file_okay=False),
    name: Optional[str] = typer.Option(None, "--name"),
    org: Optional[str] = typer.Option(None, "--org"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway", envvar="PEAGEN_GATEWAY_URL"
    ),
):
    args = {
        "operation": "doe-spec",
        "path": str(path),
        "name": name,
        "org": org,
        "force": force,
    }
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(gateway_url, json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))


# ───────────────────────────── ci ──────────────────────────
ci_app = typer.Typer(help="Create a CI pipeline file.")
init_app.add_typer(ci_app, name="ci")


@ci_app.command("run")
def run_ci(
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
):
    args = {"operation": "ci", "github": github, "force": force}
    task = _build_task(args)
    result = asyncio.run(init_handler(task))
    typer.echo(json.dumps(result, indent=2))


@ci_app.command("submit")
def submit_ci(
    github: bool = typer.Option(True, "--github/--gitlab"),
    force: bool = typer.Option(False, "--force"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY, "--gateway", envvar="PEAGEN_GATEWAY_URL"
    ),
):
    args = {"operation": "ci", "github": github, "force": force}
    task = _build_task(args)
    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(gateway_url, json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()
    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)
    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))

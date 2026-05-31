"""Command-line interface for the ALT Foundry Kernel bootloader."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer

from alt_foundry_kernel.kernel import run_kernel_transition
from alt_foundry_kernel.models import KernelState
from alt_foundry_kernel.public_audit import run_public_audit
from alt_foundry_kernel.schemas import load_schema
from alt_foundry_kernel.validation import validate_packet

app = typer.Typer(help="ALT Foundry Kernel packet tools.")


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@app.command()
def validate(packet: Annotated[Path, typer.Argument(help="Path to a packet JSON file.")]) -> None:
    """Validate a packet against schema and v1 fail-closed semantic gates."""

    report = validate_packet(_read_json(packet))
    typer.echo(report.model_dump_json(indent=2))
    if not report.ok:
        raise typer.Exit(code=1)


@app.command()
def decide(
    packet: Annotated[Path, typer.Argument(help="Path to a packet JSON file.")],
    state: Annotated[
        Path | None,
        typer.Option(
            "--state",
            help="Path to a kernel-state JSON file. Defaults to an empty state.",
        ),
    ] = None,
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Optional file path for the transition result JSON."),
    ] = None,
) -> None:
    """Run one deterministic kernel transition."""

    current_state = KernelState.model_validate(_read_json(state)) if state else KernelState()
    result = run_kernel_transition(current_state, _read_json(packet))
    payload = result.model_dump(mode="json")
    if out:
        _write_json(out, payload)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


@app.command()
def schema(name: Annotated[str, typer.Argument(help="Schema name, for example packet.")]) -> None:
    """Print a public JSON Schema."""

    typer.echo(json.dumps(load_schema(name), indent=2, sort_keys=True))


@app.command("audit-public")
def audit_public(
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Run the public-release audit with strict reporting."),
    ] = False,
    root: Annotated[
        Path | None,
        typer.Option("--root", help="Repository root to audit. Defaults to the current directory."),
    ] = None,
) -> None:
    """Audit the repository for public OSS release hygiene."""

    report = run_public_audit(root=root, strict=strict)
    typer.echo(report.to_json())
    if not report.ok:
        raise typer.Exit(code=1)


@app.command("init-example")
def init_example(
    name: Annotated[
        str,
        typer.Argument(
            help="Example name: candidate, proxy-only, admission, deprecation, transport-refresh."
        ),
    ],
    out: Annotated[Path | None, typer.Option("--out", help="Optional destination file.")] = None,
) -> None:
    """Print or write a bundled example packet."""

    mapping = {
        "candidate": "candidate_packet.json",
        "proxy-only": "proxy_only_packet.json",
        "admission": "admission_packet.json",
        "deprecation": "deprecation_packet.json",
        "transport-refresh": "transport_refresh_packet.json",
        "monitor-alarm": "monitor_alarm_packet.json",
        "rollback": "rollback_packet.json",
        "resurrection": "resurrection_packet.json",
        "bridge": "bridge_packet.json",
        "kernel-update": "kernel_update_packet.json",
    }
    filename = mapping.get(name)
    if filename is None:
        raise typer.BadParameter(f"Unknown example {name!r}.")
    source = Path(__file__).resolve().parents[2] / "examples" / filename
    payload = json.loads(source.read_text(encoding="utf-8"))
    if out:
        _write_json(out, payload)
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))

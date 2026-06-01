"""Command-line interface for the ALT Foundry Kernel reference implementation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, cast

import typer
from jsonschema import Draft202012Validator

from alt_foundry_kernel.authority import validate_authority_certificate
from alt_foundry_kernel.cara import validate_cara_certificate
from alt_foundry_kernel.cara_ext import validate_cara_process
from alt_foundry_kernel.causal import validate_causal_certificate
from alt_foundry_kernel.certificate_algebra import validate_certificate_composition
from alt_foundry_kernel.conformance import run_conformance
from alt_foundry_kernel.evaluator import validate_evaluator_hierarchy
from alt_foundry_kernel.finality import validate_finality_poua_ledger
from alt_foundry_kernel.foundry import make_dashboard, replay_transcript
from alt_foundry_kernel.foundry_control import validate_foundry_control_state
from alt_foundry_kernel.kernel import run_kernel_transition
from alt_foundry_kernel.measurement import validate_measurement_spec
from alt_foundry_kernel.mechanism import validate_mechanism_certificate
from alt_foundry_kernel.models import KernelState
from alt_foundry_kernel.non_reduction import validate_non_reduction_audit
from alt_foundry_kernel.portfolio_ext import validate_portfolio_constraints
from alt_foundry_kernel.public_audit import run_public_audit
from alt_foundry_kernel.reproduction import validate_reproduction_certificate
from alt_foundry_kernel.risk import validate_risk_certificate
from alt_foundry_kernel.root_finality import validate_root_finality_certificate
from alt_foundry_kernel.schemas import load_schema
from alt_foundry_kernel.sequential import validate_sequential_decision
from alt_foundry_kernel.transport import validate_transport_certificate
from alt_foundry_kernel.transport_ext import validate_transport_robustness
from alt_foundry_kernel.validation import validate_packet

app = typer.Typer(help="ALT Foundry Kernel packet tools.")


def _read_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@app.command()
def validate(
    kind_or_path: Annotated[
        str,
        typer.Argument(
            help="Backcompat packet path, or kind: packet, schema, evidence, state, transcript."
        ),
    ],
    path: Annotated[Path | None, typer.Argument(help="JSON file to validate.")] = None,
) -> None:
    """Validate a packet or v0.3.0 language-neutral artifact."""

    if path is None:
        report = validate_packet(_read_json(Path(kind_or_path)))
        typer.echo(report.model_dump_json(indent=2))
        if not report.ok:
            raise typer.Exit(code=1)
        return

    payload = _read_json(path)
    if kind_or_path == "packet":
        report = validate_packet(payload)
        typer.echo(report.model_dump_json(indent=2))
        if not report.ok:
            raise typer.Exit(code=1)
        return
    if kind_or_path == "state":
        state = KernelState.model_validate(payload)
        typer.echo(state.model_dump_json(indent=2))
        return
    if kind_or_path == "schema":
        Draft202012Validator.check_schema(payload)
        typer.echo(json.dumps({"ok": True}, indent=2))
        return
    if kind_or_path == "evidence":
        evidence_report = validate_measurement_spec(payload)
        typer.echo(evidence_report.model_dump_json(indent=2))
        if not evidence_report.ok:
            raise typer.Exit(code=1)
        return
    if kind_or_path == "transcript":
        ok = replay_transcript(payload)
        typer.echo(json.dumps({"ok": ok}, indent=2))
        if not ok:
            raise typer.Exit(code=1)
        return
    raise typer.BadParameter(f"Unknown validation kind {kind_or_path!r}.")


@app.command()
def certify(
    kind: Annotated[
        str,
        typer.Argument(
            help=(
                "Certificate kind: measurement, transport, risk, authority, "
                "root-finality, causal, cara, reproduction, non-reduction, "
                "mechanism, evaluator, finality, sequential, transport-ext, "
                "certificate-algebra, portfolio-ext, foundry-control, cara-ext."
            )
        ),
    ],
    path: Annotated[Path, typer.Argument(help="Certificate JSON file.")],
) -> None:
    """Run a module-level ALT certificate checker."""

    payload = _read_json(path)
    checkers = {
        "measurement": validate_measurement_spec,
        "transport": validate_transport_certificate,
        "risk": validate_risk_certificate,
        "authority": validate_authority_certificate,
        "root-finality": validate_root_finality_certificate,
        "causal": validate_causal_certificate,
        "cara": validate_cara_certificate,
        "reproduction": validate_reproduction_certificate,
        "non-reduction": validate_non_reduction_audit,
        "mechanism": validate_mechanism_certificate,
        "evaluator": validate_evaluator_hierarchy,
        "finality": validate_finality_poua_ledger,
        "sequential": validate_sequential_decision,
        "transport-ext": validate_transport_robustness,
        "certificate-algebra": validate_certificate_composition,
        "portfolio-ext": validate_portfolio_constraints,
        "foundry-control": validate_foundry_control_state,
        "cara-ext": validate_cara_process,
    }
    checker = checkers.get(kind)
    if checker is None:
        raise typer.BadParameter(f"Unknown certificate kind {kind!r}.")
    report = checker(payload)
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


@app.command()
def replay(
    transcript: Annotated[Path, typer.Argument(help="Path to a golden decision transcript.")]
) -> None:
    """Replay a language-neutral decision transcript."""

    ok = replay_transcript(_read_json(transcript))
    typer.echo(json.dumps({"ok": ok}, indent=2))
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def dashboard(
    state: Annotated[Path, typer.Argument(help="Path to a kernel-state JSON file.")]
) -> None:
    """Render a foundry-control dashboard JSON summary."""

    typer.echo(json.dumps(make_dashboard(_read_json(state)), indent=2, sort_keys=True))


@app.command()
def conformance(
    fixtures: Annotated[
        Path,
        typer.Option("--fixtures", help="Directory containing golden transcript fixtures."),
    ] = Path("conformance"),
    level: Annotated[
        str,
        typer.Option("--level", help="Conformance level: L0, L1, L2, L3, L4, or L5."),
    ] = "L5",
) -> None:
    """Run language-neutral conformance replay and certificate fixtures."""

    report = run_conformance(fixtures, level=level)
    typer.echo(report.to_json())
    if not report.ok:
        raise typer.Exit(code=1)


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

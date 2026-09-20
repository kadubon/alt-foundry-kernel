"""Thin opt-in CLI wrappers. JSON is inert; only ingest changes local history."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from .bridge import at_history
from .cait_export import export_cait
from .checker import check_plan
from .contracts import Contract, Plan, Qualification
from .examples import example, history_example
from .formation import Formation, form
from .interchange import ccr_tasks, vek_demand
from .lifecycle import Journal, ingest, replay
from .planning import comparison_report, select
from .qualification import qualify
from .wire import Source, encoded, loads

app = typer.Typer(help="Experimental finite collective reuse; no execution or settlement.")


def read(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        raw = stream.read(2000001)
    return loads(raw)


def emit(value: Any, out: Path | None) -> None:
    raw = encoded(value) + "\n"
    if out is None:
        typer.echo(raw, nl=False)
    else:
        out.write_text(raw, encoding="utf-8", newline="\n")


@app.command("example")
def example_command(out: Path | None = None, history: bool = False) -> None:
    emit(history_example() if history else example(), out)


@app.command("form")
def form_command(source: Path, out: Path | None = None) -> None:
    emit(form(Formation.model_validate(read(source))), out)


@app.command("qualify")
def qualify_command(source: Path, at: int, out: Path | None = None) -> None:
    row = Qualification.model_validate(read(source))
    emit(
        {
            "qualified": qualify(row.request, row.candidate, row.offer, at),
            "receiver": row.offer.receiver,
            "execution_authority": None,
        },
        out,
    )


@app.command("inspect")
@app.command("replay")
def replay_command(
    source: Path, cutoff: int, out: Path | None = None, corrected: bool = False
) -> None:
    emit(replay(Journal.model_validate(read(source)), cutoff, corrected=corrected), out)


def context(source: Path, history: Path | None) -> Contract:
    contract = Contract.model_validate(read(source))
    return (
        contract if history is None else at_history(contract, Journal.model_validate(read(history)))
    )


@app.command("plan")
def plan_command(source: Path, out: Path | None = None, history: Path | None = None) -> None:
    emit(select(context(source, history)), out)


@app.command("check-plan")
def check_command(
    source: Path, plan: Path, out: Path | None = None, history: Path | None = None
) -> None:
    emit(check_plan(context(source, history), Plan.model_validate(read(plan))), out)


@app.command("compare")
def compare_command(source: Path, out: Path | None = None, history: Path | None = None) -> None:
    emit(comparison_report(context(source, history)), out)


@app.command("ingest")
def ingest_command(source: Path, event: Path, store: Path, expected: str) -> None:
    emit(
        ingest(
            store,
            Journal.model_validate(read(source)),
            Source.model_validate(read(event)),
            expected,
        ),
        None,
    )


@app.command("export")
def export_command(
    source: Path,
    kind: str,
    out: Path | None = None,
    plan: Path | None = None,
    created_at: str = "",
    revision: str = "",
    cutoff: int = 0,
    time_unit: str = "",
    limits: Path | None = None,
) -> None:
    if kind == "cait":
        if limits is None or not time_unit:
            raise ValueError("CAIT mapping requires named clock and resource limits")
        result = export_cait(Journal.model_validate(read(source)), cutoff, time_unit, read(limits))
    else:
        if plan is None:
            raise ValueError("export requires independently checkable plan")
        contract = Contract.model_validate(read(source))
        checked = Plan.model_validate(read(plan))
        if kind == "ccr" and created_at and revision:
            result = ccr_tasks(contract, checked, created_at, revision)
        elif kind == "vek":
            result = vek_demand(contract, checked)
        else:
            raise ValueError("unknown export or missing original revision/time")
    emit(result, out)

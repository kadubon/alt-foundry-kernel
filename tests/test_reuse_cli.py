from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from alt_foundry_kernel.cli import app
from alt_foundry_kernel.reuse.examples import contract_example, formation_example, history_example
from alt_foundry_kernel.reuse.lifecycle import empty
from alt_foundry_kernel.reuse.planning import select
from alt_foundry_kernel.reuse.wire import digest, encoded


def test_all_explicit_commands(tmp_path: Path) -> None:
    runner = CliRunner()
    contract = contract_example(1)
    history = history_example()
    blank = empty(history.scope, history.study)
    payloads = {
        "contract": contract,
        "plan": select(contract),
        "formation": formation_example(),
        "qualification": contract.qualifications[0],
        "history": history,
        "empty": blank,
        "event": history.events[0],
        "limits": {"resource": "100"},
    }
    for name, payload in payloads.items():
        (tmp_path / (name + ".json")).write_text(encoded(payload), encoding="utf-8")

    def file(name: str) -> str:
        return str(tmp_path / (name + ".json"))

    calls = [
        ["example"],
        ["example", "--history"],
        ["form", file("formation")],
        ["qualify", file("qualification"), "3"],
        ["inspect", file("history"), "20"],
        ["replay", file("history"), "20", "--corrected"],
        ["plan", file("contract")],
        ["check-plan", file("contract"), file("plan")],
        ["compare", file("contract")],
        ["export", file("contract"), "vek", "--plan", file("plan")],
        [
            "export",
            file("contract"),
            "ccr",
            "--plan",
            file("plan"),
            "--created-at",
            "2026-09-20T00:00:00Z",
            "--revision",
            "source-revision",
        ],
        [
            "export",
            file("history"),
            "cait",
            "--cutoff",
            "20",
            "--time-unit",
            "synthetic-tick",
            "--limits",
            file("limits"),
        ],
        ["ingest", file("empty"), file("event"), file("store"), digest(blank)],
    ]
    for call in calls:
        result = runner.invoke(app, ["reuse", *call])
        assert result.exit_code == 0, (call, result.output, result.exception)
        assert isinstance(json.loads(result.output), dict)
    result = runner.invoke(app, ["reuse", "form", file("formation"), "--out", file("formed")])
    assert result.exit_code == 0 and Path(file("formed")).is_file()
    for args in [
        ["export", file("history"), "cait"],
        ["export", file("contract"), "vek"],
        ["export", file("contract"), "invalid", "--plan", file("plan")],
    ]:
        assert runner.invoke(app, ["reuse", *args]).exit_code != 0

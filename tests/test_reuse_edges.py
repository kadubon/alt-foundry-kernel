from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from alt_foundry_kernel.reuse import installed_check
from alt_foundry_kernel.reuse.cait_export import export_cait
from alt_foundry_kernel.reuse.checker import check_plan
from alt_foundry_kernel.reuse.contracts import Plan
from alt_foundry_kernel.reuse.examples import contract_example, formation_example, history_example
from alt_foundry_kernel.reuse.formation import form, reconstruct
from alt_foundry_kernel.reuse.interchange import import_vek, pinned
from alt_foundry_kernel.reuse.lifecycle import Journal, empty, replay
from alt_foundry_kernel.reuse.planning import select
from alt_foundry_kernel.reuse.premises import identity, validate
from alt_foundry_kernel.reuse.wire import digest, envelope


def amend_last(journal: Journal, **changes: Any) -> None:
    raw = journal.events[-1].read()
    raw.update(changes)
    journal.events[-1] = envelope(raw)


@pytest.mark.parametrize(
    "changes",
    [
        {"kind": "cost"},
        {"kind": "qualify"},
        {"kind": "qualify", "offer_digest": None},
        {"attempt": "missing"},
        {"receiver": "wrong"},
        {"time": 100, "recorded": 100},
        {"kind": "correct", "target": "missing"},
    ],
)
def test_lifecycle_incomplete_evidence_fails(changes: dict[str, Any]) -> None:
    journal = history_example()
    amend_last(journal, **changes)
    with pytest.raises(ValueError):
        replay(journal, 1000)


def test_failure_and_unknown_completion_are_distinct() -> None:
    journal = history_example()
    amend_last(journal, outcome="unknown")
    state = replay(journal, 20)
    assert len(state["successful_uses"]) == 3 and state["unresolved"]
    amend_last(journal, outcome="failure")
    state = replay(journal, 20)
    assert len(state["successful_uses"]) == 3
    assert len(state["eligible"]) == 3 and not state["unresolved"]
    raw = journal.events[-1].read()
    raw.update(id="late-success", outcome="success", time=21, recorded=21, previous=digest(journal))
    journal.events.append(envelope(raw))
    assert replay(journal, 20)["successful_uses"] == state["successful_uses"]
    with pytest.raises(ValueError, match="unique request"):
        replay(journal, 22)


def test_attempt_and_cost_id_conflict() -> None:
    journal = history_example()
    raw = journal.events[-2].read()
    raw.update(id="retry-request", time=12, recorded=12, previous=digest(journal))
    journal.events.append(envelope(raw))
    with pytest.raises(ValueError, match="attempt"):
        replay(journal, 20)
    journal = history_example()
    raw = journal.events[0].read()
    raw.update(id="charge-copy", time=12, recorded=12, quantity="99", previous=digest(journal))
    journal.events.append(envelope(raw))
    with pytest.raises(ValueError, match="physical cost"):
        replay(journal, 20)


@pytest.mark.parametrize("field", ["artifact", "receiver", "dependencies", "valid_until"])
def test_qualification_event_requires_actual_source(field: str) -> None:
    original = history_example()
    index = next(
        i for i, source in enumerate(original.events) if source.read()["kind"] == "qualify"
    )
    journal = original.model_copy(deep=True)
    journal.events = journal.events[: index + 1]
    changes = {"artifact": "0" * 64, "receiver": "C", "dependencies": ["0" * 64], "valid_until": 99}
    amend_last(journal, **{field: changes[field]})
    with pytest.raises(ValueError):
        replay(journal, 20)


def test_stale_refresh_cannot_clear_failure() -> None:
    journal = history_example()
    amend_last(journal, outcome="failure")
    raw = next(source.read() for source in journal.events if source.read()["id"] == "qualify-use-3")
    raw.update(id="stale-refresh", kind="refresh", time=12, recorded=12, previous=digest(journal))
    journal.events.append(envelope(raw))
    with pytest.raises(ValueError, match="after scoped"):
        replay(journal, 20)


def test_vek_clock_and_counter_contracts() -> None:
    report = pinned("vek-report-positive.json")
    args = [
        report["scope"],
        report["snapshot_revision"],
        report["time_origin"],
        report["slot_seconds"],
    ]
    assert import_vek(report, *args)["counters_replayed"] is False
    with pytest.raises(ValueError):
        import_vek(report, args[0], args[1], "other", args[3])
    report["local_accounting"]["unfinished"] = 0
    with pytest.raises(ValueError):
        import_vek(report, *args)
    with pytest.raises(ValueError):
        pinned("../../outside.json")


def test_partial_cait_mapping_does_not_repair_missing_data() -> None:
    journal = history_example()
    for cutoff, limits in ((3, {"resource": "100"}), (20, {})):
        result = export_cait(journal, cutoff, "tick", limits)
        assert result["native_bundle"] is None and result["unmapped_obligations"]
    result = export_cait(empty(journal.scope, journal.study), 20, "tick", {})
    assert result["native_bundle"] is None
    raw = journal.events[-1].read()
    raw.update(id="withdraw", kind="withdraw", time=12, recorded=12, previous=digest(journal))
    journal.events.append(envelope(raw))
    assert export_cait(journal, 20, "tick", {"resource": "100"})["native_bundle"] is not None


def test_receiver_bound_and_redundant_offer() -> None:
    contract = contract_example()
    old = select(contract)
    addition = contract.options[0].model_copy(deep=True)
    addition.id = "redundant-scratch"
    contract.options.append(addition)
    plan = select(contract)
    assert plan.score == old.score
    for i in range(9):
        opportunity = contract.opportunities[0].model_copy(deep=True)
        opportunity.id, opportunity.receiver = f"extra-{i}", f"receiver-{i}"
        contract.opportunities.append(opportunity)
    with pytest.raises(ValueError, match="receiver bound"):
        validate(contract)


def test_checker_capacity_floor_unknown_incumbent() -> None:
    contract = contract_example()
    plan = select(contract)
    contract.capacities["verifier"] = 0
    plan.contract_digest = identity(contract)
    with pytest.raises(ValueError, match="resource"):
        check_plan(contract, plan)
    plan.score = None
    with pytest.raises(ValueError, match="incumbent"):
        check_plan(contract, plan)
    with pytest.raises(ValueError):
        Plan.model_validate({**plan.model_dump(), "settlement": "approved"})


def test_reconstruction_identity_and_inert_dataflow() -> None:
    request = formation_example()
    candidate = form(request)
    candidate.representation[0].primitive = "changed"
    with pytest.raises(ValueError):
        reconstruct(request, candidate)
    # A previous output reference is typed, but never executed by candidate formation.
    for i, source in enumerate(request.sources):
        raw = source.read()
        raw["steps"].append(
            {"primitive": "identity", "arguments": [{"kind": "reference", "value": 0}]}
        )
        request.sources[i] = envelope(raw)
    assert reconstruct(request, form(request))


def test_installed_check_logic_with_packaged_resource_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("ccr")
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "examples", tmp_path / "legacy_examples")
    shutil.copytree(root / "conformance", tmp_path / "legacy_conformance")
    monkeypatch.setattr(installed_check, "files", lambda name: tmp_path)
    result = installed_check.run()
    assert result["break_even_costs"] == ["5", "10", "15", "16"]
    assert result["integration"]["cait_check"]["status"] == "checked"
    assert json.loads(json.dumps(result))["runtime_sockets"] == "blocked"

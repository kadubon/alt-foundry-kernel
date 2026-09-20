from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from alt_foundry_kernel.reuse.bridge import at_history, inspect_kernel, replan
from alt_foundry_kernel.reuse.cait_export import export_cait
from alt_foundry_kernel.reuse.examples import contract_example, history_example
from alt_foundry_kernel.reuse.lifecycle import Event, Journal, empty, ingest, replay
from alt_foundry_kernel.reuse.wire import digest, encoded, envelope


def append(journal: Journal, **fields: Any) -> None:
    previous = Event.model_validate(journal.events[-1].read())
    raw = previous.model_dump()
    raw.update(
        id="next", time=12, recorded=12, kind="expire", qualification=None, previous=digest(journal)
    )
    raw.update(fields)
    journal.events.append(envelope(Event.model_validate(raw)))


def test_unique_uses_stock_and_source_round_trip() -> None:
    journal = history_example()
    first = replay(journal, 20)
    assert len(first["stock"]) == 1
    assert len(first["successful_uses"]) == 4
    assert not first["unresolved"]
    assert replay(Journal.model_validate_json(encoded(journal)), 20) == first
    journal.events.append(journal.events[-1])
    assert replay(journal, 20) == first


def test_expiry_withdrawal_keeps_history_and_replans() -> None:
    journal = history_example()
    last = journal.events[-1].read()
    last["outcome"] = "failure"
    journal.events[-1] = envelope(last)
    append(journal)
    state = replay(journal, 20)
    assert len(state["eligible"]) == 3
    assert len(state["successful_uses"]) == 3
    contract = contract_example()
    contract.initial_revision = digest(journal)
    contract.checkpoint = contract.evidence_cutoff = 20
    contract.sunk_cost_ids = list(state["costs"])
    plan = replan(contract, journal)
    assert "reuse-3" not in plan.selected and "scratch-3" in plan.selected
    append(journal, id="withdraw", kind="withdraw", time=13, recorded=13)
    state = replay(journal, 20)
    assert not state["eligible"]
    assert len(state["stock"]) == 1 and len(state["successful_uses"]) == 3


def test_completed_service_is_not_forecast_again() -> None:
    journal = history_example()
    contract = contract_example()
    contract.initial_revision = digest(journal)
    contract.checkpoint = contract.evidence_cutoff = 20
    contract.sunk_cost_ids = list(replay(journal, 20)["costs"])
    plan = replan(contract, journal)
    assert plan.selected == []
    assert plan.score is not None
    assert plan.score.scenario_net == {"deterministic": "0"}
    assert plan.score.lifecycle_cost == "16"


def test_corrected_cost_never_rewrites_as_of() -> None:
    journal = history_example()
    append(journal, kind="correct", target="charge-formation", quantity="14")
    assert replay(journal, 11)["costs"]["formation"]["amount"] == "12"
    assert replay(journal, 20)["costs"]["formation"]["amount"] == "12"
    assert replay(journal, 20, corrected=True)["costs"]["formation"]["amount"] == "14"
    append(journal, id="second-correction", kind="correct", target="charge-formation")
    with pytest.raises(ValueError, match="conflicting"):
        replay(journal, 20)


@pytest.mark.parametrize(
    "fields",
    [
        {"previous": "0" * 64},
        {"scope": "other"},
        {"study": "other"},
        {"recorded": 1},
        {"quantity": "-1"},
        {"origin": {"endogenous": "1", "external": "1", "unresolved": "0"}},
    ],
)
def test_bad_journal_envelope(fields: dict[str, Any]) -> None:
    journal = history_example()
    raw = journal.events[-1].read()
    raw.update(fields)
    journal.events[-1] = envelope(raw)
    with pytest.raises(ValueError):
        replay(journal, 20)


def test_conflicting_retry_and_missing_cost() -> None:
    journal = history_example()
    raw = journal.events[-1].read()
    raw["outcome"] = "failure"
    journal.events.append(envelope(raw))
    with pytest.raises(ValueError, match="conflicting"):
        replay(journal, 20)
    journal = history_example()
    append(journal, kind="formation", outcome="failure", required_cost_ids=["missing"])
    state = replay(journal, 20)
    assert "missing-cost:missing" in state["unresolved"]
    contract = contract_example()
    contract.initial_revision = digest(journal)
    contract.sunk_cost_ids = list(state["costs"])
    contract.checkpoint = contract.evidence_cutoff = 20
    assert replan(contract, journal).score is None


def test_new_mission_and_sunk_cost_reset_rejected() -> None:
    journal = history_example()
    contract = contract_example()
    with pytest.raises(ValueError, match="checkpoint"):
        at_history(contract, journal)
    contract.initial_revision = digest(journal)
    with pytest.raises(ValueError, match="historical charge"):
        at_history(contract, journal)


def test_ingest_revision_and_retry(tmp_path: Path) -> None:
    history = history_example()
    journal = empty(history.scope, history.study)
    target = tmp_path / "journal.json"
    event = history.events[0]
    assert ingest(target, journal, event, digest(journal))["writes"]
    persisted = Journal.model_validate_json(target.read_text())
    assert not ingest(target, journal, event, digest(persisted))["writes"]
    with pytest.raises(ValueError, match="stale"):
        ingest(target, journal, history.events[1], digest(journal))
    raw = event.read()
    raw["quantity"] = "99"
    with pytest.raises(ValueError, match="conflicting"):
        ingest(target, journal, envelope(raw), digest(persisted))


def test_cait_partial_and_native_history() -> None:
    journal = history_example()
    report = export_cait(journal, 20, "synthetic-tick", {"resource": "100"})
    assert report["native_bundle"] is not None
    assert report["source_journal"] == journal.model_dump()
    append(journal)
    report = export_cait(journal, 20, "synthetic-tick", {"resource": "100"})
    assert report["native_bundle"] is None
    assert "unmapped-event:expire" in report["unmapped_obligations"]


def test_legacy_capital_is_not_current_receiver_stock() -> None:
    from json import loads

    from alt_foundry_kernel import KernelState, run_kernel_transition

    root = Path(__file__).resolve().parents[1]
    packet = loads((root / "examples/admission_packet.json").read_text())
    first = run_kernel_transition(KernelState(), packet)
    repeated = run_kernel_transition(first.next_state, packet)
    assert repeated.next_state.certified_capital == 2 * first.next_state.certified_capital
    deprecation = loads((root / "examples/deprecation_packet.json").read_text())
    withdrawn = run_kernel_transition(first.next_state, deprecation)
    view = inspect_kernel(withdrawn.next_state)
    assert view["legacy_cumulative_capital"] == first.next_state.certified_capital
    assert view["legacy_current_tokens"] == []
    assert view["receiver_qualified_stock"] is None

from __future__ import annotations

import json
from pathlib import Path

from alt_foundry_kernel import Decision, KernelState, run_kernel_transition, validate_packet
from alt_foundry_kernel.constants import LifecycleState

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _load(name: str) -> dict[str, object]:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def test_valid_candidate_enters_candidate_queue_without_capital() -> None:
    result = run_kernel_transition(KernelState(), _load("candidate_packet.json"))

    assert result.decision == Decision.DEFER
    assert result.next_state.certified_capital == 0.0
    assert len(result.next_state.candidate_queue) == 1
    assert result.next_state.settlement_ledger == []


def test_proxy_only_admission_goes_to_exploration_only() -> None:
    result = run_kernel_transition(KernelState(), _load("proxy_only_packet.json"))

    assert result.decision == Decision.DEFER
    assert result.next_state.certified_capital == 0.0
    assert len(result.next_state.exploration_ledger) == 1
    assert result.next_state.settlement_ledger == []


def test_positive_admission_requires_all_predicates_and_finality() -> None:
    result = run_kernel_transition(KernelState(), _load("admission_packet.json"))

    assert result.decision == Decision.ADMIT
    assert result.next_state.certified_capital == 6.5
    assert result.next_state.admitted_tokens == ["tok-workflow-triage"]
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.ACTIVE
    assert len(result.next_state.settlement_ledger) == 1


def test_missing_cost_upper_bound_fails_closed() -> None:
    packet = _load("admission_packet.json")
    bounds = packet["bounds"]
    assert isinstance(bounds, dict)
    bounds.pop("cost_upper_bound")

    report = validate_packet(packet)
    result = run_kernel_transition(KernelState(), packet)

    assert not report.ok
    assert result.decision == Decision.DEFER
    assert result.next_state.certified_capital == 0.0
    assert result.next_state.settlement_ledger == []


def test_deprecation_records_negative_registry_without_capital_increase() -> None:
    state = KernelState(
        admitted_tokens=["tok-workflow-triage"],
        token_states={"tok-workflow-triage": LifecycleState.ACTIVE},
        certified_capital=6.5,
    )

    result = run_kernel_transition(state, _load("deprecation_packet.json"))

    assert result.decision == Decision.DEPRECATE
    assert result.next_state.certified_capital == 6.5
    assert result.next_state.admitted_tokens == []
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.DEPRECATED
    assert len(result.next_state.negative_registry) == 1


def test_transport_refresh_allowed_from_suspended_to_active() -> None:
    state = KernelState(token_states={"tok-workflow-triage": LifecycleState.SUSPENDED})

    result = run_kernel_transition(state, _load("transport_refresh_packet.json"))

    assert result.decision == Decision.ADMIT
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.ACTIVE
    assert result.next_state.certified_capital == 0.0


def test_rollback_allowed_from_active_and_charges_reserve() -> None:
    state = KernelState(
        admitted_tokens=["tok-workflow-triage"],
        token_states={"tok-workflow-triage": LifecycleState.ACTIVE},
        certified_capital=6.5,
    )
    packet = _load("rollback_packet.json")

    result = run_kernel_transition(state, packet)

    assert result.decision == Decision.ROLLBACK
    assert result.next_state.certified_capital == 5.0
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.SUSPENDED


def test_resurrection_without_admission_grade_evidence_returns_to_candidate() -> None:
    state = KernelState(token_states={"tok-workflow-triage": LifecycleState.DEPRECATED})
    packet = _load("resurrection_packet.json")

    result = run_kernel_transition(state, packet)

    assert result.decision == Decision.RESURRECT
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.CANDIDATE
    assert result.next_state.certified_capital == 0.0
    assert result.next_state.settlement_ledger == []


def test_resurrection_with_admission_grade_current_evidence_can_add_capital() -> None:
    state = KernelState(token_states={"tok-workflow-triage": LifecycleState.DEPRECATED})
    packet = _load("resurrection_packet.json")
    admission = _load("admission_packet.json")
    packet["declaration"] = {
        **admission["declaration"],  # type: ignore[dict-item]
        "old_negative_certificate_id": "pkt-deprecation-001",
    }
    packet["evidence"] = {
        **admission["evidence"],  # type: ignore[dict-item]
        "overwriting_evidence": "new heldout certification split",
    }
    packet["validity"] = admission["validity"]

    result = run_kernel_transition(state, packet)

    assert result.decision == Decision.RESURRECT
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.ACTIVE
    assert result.next_state.certified_capital == 3.0


def test_non_admission_packet_types_fail_closed_when_required_fields_are_missing() -> None:
    cases = [
        ("transport_refresh_packet.json", ("declaration", "bridge")),
        ("monitor_alarm_packet.json", ("evidence", "alarm_statistic")),
        ("deprecation_packet.json", ("fallback", "resurrection_rule")),
        ("rollback_packet.json", ("bounds", "reserve_charge")),
        ("resurrection_packet.json", ("evidence", "overwriting_evidence")),
        ("bridge_packet.json", ("declaration", "bridge")),
        ("kernel_update_packet.json", ("fallback", "rollback_path")),
    ]
    state = KernelState(
        admitted_tokens=["tok-workflow-triage"],
        token_states={
            "tok-workflow-triage": LifecycleState.ACTIVE,
            "kernel-alt-bootloader": LifecycleState.ACTIVE,
        },
        certified_capital=6.5,
    )
    for filename, path in cases:
        packet = _load(filename)
        parent = packet[path[0]]
        assert isinstance(parent, dict)
        parent.pop(path[1])

        report = validate_packet(packet)
        result = run_kernel_transition(state, packet)

        assert not report.ok, filename
        assert result.next_state.certified_capital == 6.5, filename
        assert result.next_state.settlement_ledger == [], filename


def test_monitor_alarm_requires_active_or_pending_settlement_state() -> None:
    state = KernelState(token_states={"tok-workflow-triage": LifecycleState.CANDIDATE})
    result = run_kernel_transition(state, _load("monitor_alarm_packet.json"))

    assert result.decision == Decision.SUSPEND
    assert result.next_state.certified_capital == 0.0
    assert result.next_state.token_states["tok-workflow-triage"] == LifecycleState.SUSPENDED
    assert result.next_state.settlement_ledger == []


def test_bridge_and_kernel_update_are_non_capital_audit_records() -> None:
    state = KernelState(token_states={"kernel-alt-bootloader": LifecycleState.ACTIVE})

    bridge = run_kernel_transition(state, _load("bridge_packet.json"))
    update = run_kernel_transition(state, _load("kernel_update_packet.json"))

    assert bridge.decision == Decision.DEFER
    assert update.decision == Decision.DEFER
    assert bridge.next_state.certified_capital == 0.0
    assert update.next_state.certified_capital == 0.0
    assert len(bridge.next_state.audit_log) == 1
    assert len(update.next_state.audit_log) == 1


def test_cara_target_crossing_fields_are_conditionally_required() -> None:
    base_report = validate_packet(_load("admission_packet.json"))
    assert base_report.predicates["NetLowerBoundOK"] is True
    assert base_report.predicates["TargetValidityOK"] is None
    assert base_report.predicates["BaselineEnvelopeOK"] is None
    assert base_report.predicates["QuorumOK"] is True
    assert base_report.predicates["RuntimeWitnessOK"] is True

    packet = _load("admission_packet.json")
    declaration = packet["declaration"]
    assert isinstance(declaration, dict)
    declaration["cara"] = {"claims_target_crossing": True}

    report = validate_packet(packet)

    assert not report.ok
    assert any(issue.code == "cara-required-field-missing" for issue in report.issues)
    assert report.predicates["TargetValidityOK"] is False
    assert report.predicates["BaselineEnvelopeOK"] is False

    declaration["cara"] = {
        "claims_target_crossing": True,
        "asi_target_id": "asi-target-demo",
        "capability_basis_id": "capability-basis-demo",
        "target_validity_certificate": "target-validity-demo",
        "baseline_upper_envelope": "baseline-envelope-demo",
        "target_membership_proof": "target-membership-demo",
        "viability_witness": "viability-demo",
        "time_to_target_claim": "time-to-target-demo",
    }

    fixed = validate_packet(packet)
    assert fixed.ok
    assert fixed.predicates["TargetValidityOK"] is True
    assert fixed.predicates["BaselineEnvelopeOK"] is True

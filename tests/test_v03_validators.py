from __future__ import annotations

import copy
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from alt_foundry_kernel.cara_ext import validate_cara_process
from alt_foundry_kernel.certificate_algebra import validate_certificate_composition
from alt_foundry_kernel.evaluator import validate_evaluator_hierarchy
from alt_foundry_kernel.finality import validate_finality_poua_ledger
from alt_foundry_kernel.foundry_control import validate_foundry_control_state
from alt_foundry_kernel.mechanism import validate_mechanism_certificate
from alt_foundry_kernel.non_reduction import validate_non_reduction_audit
from alt_foundry_kernel.portfolio_ext import validate_portfolio_constraints
from alt_foundry_kernel.reports import CertificateReport
from alt_foundry_kernel.sequential import validate_sequential_decision
from alt_foundry_kernel.transport_ext import validate_transport_robustness

ROOT = Path(__file__).resolve().parents[1]
CERTS = ROOT / "examples" / "certificates"


Checker = Callable[[Mapping[str, Any]], CertificateReport]


def _load(name: str) -> dict[str, Any]:
    return json.loads((CERTS / name).read_text(encoding="utf-8"))


def _mutated(name: str) -> dict[str, Any]:
    return copy.deepcopy(_load(name))


def test_v03_certificate_examples_pass() -> None:
    checks: dict[str, Checker] = {
        "non_reduction_audit.json": validate_non_reduction_audit,
        "mechanism_certificate.json": validate_mechanism_certificate,
        "evaluator_hierarchy.json": validate_evaluator_hierarchy,
        "finality_poua_ledger.json": validate_finality_poua_ledger,
        "sequential_decision.json": validate_sequential_decision,
        "transport_robustness.json": validate_transport_robustness,
        "certificate_composition.json": validate_certificate_composition,
        "portfolio_constraints.json": validate_portfolio_constraints,
        "foundry_control_state.json": validate_foundry_control_state,
        "cara_process.json": validate_cara_process,
    }
    for filename, checker in checks.items():
        assert checker(_load(filename)).ok, filename


def test_non_reduction_shortcuts_cannot_replace_liquidity_certification() -> None:
    payload = _mutated("non_reduction_audit.json")
    payload["shortcuts"][0]["used_as_certification"] = True

    report = validate_non_reduction_audit(payload)

    assert not report.ok
    assert report.predicates["ShortcutFree"] is False


def test_mechanism_certificate_rejects_self_certification() -> None:
    payload = _mutated("mechanism_certificate.json")
    payload["self_certification"]["self_certified"] = True

    report = validate_mechanism_certificate(payload)

    assert not report.ok
    assert report.predicates["SelfCertificationFree"] is False


def test_evaluator_hierarchy_rejects_cycles_and_self_edges() -> None:
    payload = _mutated("evaluator_hierarchy.json")
    payload["evaluation_edges"].append(
        {"evaluator": "candidate-evaluator", "subject": "gold-evaluator"}
    )
    payload["evaluation_edges"].append(
        {"evaluator": "candidate-evaluator", "subject": "candidate-evaluator"}
    )

    report = validate_evaluator_hierarchy(payload)

    assert not report.ok
    assert report.predicates["EvaluatorGraphAcyclic"] is False
    assert report.predicates["SelfCertificationCycleFree"] is False


def test_finality_poua_weight_cannot_replace_epistemic_authority() -> None:
    payload = _mutated("finality_poua_ledger.json")
    payload["poua_ledger"]["used_as_epistemic_authority"] = True

    report = validate_finality_poua_ledger(payload)

    assert not report.ok
    assert report.predicates["PoUANotEpistemicAuthority"] is False


def test_sequential_sampling_requires_positive_evsi_net_of_cost() -> None:
    payload = _mutated("sequential_decision.json")
    payload["sampling"]["evsi_lower_bound"] = 0.25

    report = validate_sequential_decision(payload)

    assert not report.ok
    assert report.predicates["SettleOrSampleOK"] is False


def test_transport_robustness_fails_without_support_or_radius_evidence() -> None:
    payload = _mutated("transport_robustness.json")
    payload["support"]["status"] = "uncovered"
    payload["wasserstein"]["radius_upper_bound"] = 2.0

    report = validate_transport_robustness(payload)

    assert not report.ok
    assert report.predicates["SupportCoverageOK"] is False
    assert report.predicates["WassersteinRadiusOK"] is False


def test_certificate_algebra_rejects_naive_or_mismatched_composition() -> None:
    payload = _mutated("certificate_composition.json")
    payload["composition"]["naive"] = True
    payload["certificates"][1]["estimand_id"] = "different-estimand"

    report = validate_certificate_composition(payload)

    assert not report.ok
    assert report.predicates["NaiveCompositionRejected"] is False
    assert report.predicates["CommonEstimandOK"] is False


def test_portfolio_constraints_detect_conflicts_and_cherry_picking() -> None:
    payload = _mutated("portfolio_constraints.json")
    payload["selection"] = ["tok-a", "tok-b"]
    payload["cherry_picking"]["status"] = "failed"

    report = validate_portfolio_constraints(payload)

    assert not report.ok
    assert report.predicates["ConflictFreeSelection"] is False
    assert report.predicates["CherryPickingCleared"] is False


def test_foundry_control_enforces_capacity_and_conservative_exploration() -> None:
    payload = _mutated("foundry_control_state.json")
    payload["bottleneck"]["min_cut_capacity"] = 1.0
    payload["exploration"]["capital_at_risk_upper_bound"] = 5.0

    report = validate_foundry_control_state(payload)

    assert not report.ok
    assert report.predicates["BottleneckCapacityOK"] is False
    assert report.predicates["CapitalConservativeExploration"] is False


def test_cara_process_requires_target_validity_viability_and_time_gain() -> None:
    payload = _mutated("cara_process.json")
    payload["target"]["status"] = "invalid"
    payload["viability_control"]["status"] = "missing"
    payload["time_to_target"]["acceleration_lower_bound"] = 0.0

    report = validate_cara_process(payload)

    assert not report.ok
    assert report.predicates["TargetValidityOK"] is False
    assert report.predicates["ViabilityControlledOK"] is False
    assert report.predicates["TimeToTargetImprovementOK"] is False

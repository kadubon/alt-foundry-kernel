from __future__ import annotations

import json
from pathlib import Path

from alt_foundry_kernel import (
    capacity_capped_growth,
    compute_portfolio_capital,
    compute_raw_net_capital,
    validate_authority_certificate,
    validate_cara_certificate,
    validate_causal_certificate,
    validate_dependency_closure,
    validate_measurement_spec,
    validate_reproduction_certificate,
    validate_risk_certificate,
    validate_root_finality_certificate,
    validate_transport_certificate,
)
from alt_foundry_kernel.statistics import (
    bounded_mean_report,
    empirical_bernstein_lower_bound,
    post_selection_adjusted_confidence,
)

ROOT = Path(__file__).resolve().parents[1]
CERTS = ROOT / "examples" / "certificates"


def _load(name: str) -> dict[str, object]:
    return json.loads((CERTS / name).read_text(encoding="utf-8"))


def test_certificate_examples_pass_module_checkers() -> None:
    checks = [
        (validate_measurement_spec, "measurement_spec.json"),
        (validate_transport_certificate, "transport_certificate.json"),
        (validate_risk_certificate, "risk_ledger.json"),
        (validate_authority_certificate, "authority_certificate.json"),
        (validate_root_finality_certificate, "root_finality_record.json"),
        (validate_causal_certificate, "causal_certificate.json"),
        (validate_cara_certificate, "cara_claim.json"),
        (validate_reproduction_certificate, "reproduction_record.json"),
    ]
    for checker, filename in checks:
        report = checker(_load(filename))
        assert report.ok, filename


def test_measurement_missing_firewall_fails_closed() -> None:
    spec = _load("measurement_spec.json")
    spec.pop("firewall")

    report = validate_measurement_spec(spec)

    assert not report.ok
    assert any(issue.path == "firewall.status" for issue in report.issues)


def test_proxy_only_causal_certificate_is_not_settlement_grade() -> None:
    certificate = _load("causal_certificate.json")
    estimand = certificate["estimand"]
    assert isinstance(estimand, dict)
    estimand["estimand_type"] = "proxy-only"

    report = validate_causal_certificate(certificate)

    assert report.ok
    assert report.predicates["SettlementGrade"] is False


def test_cara_claim_requires_positive_time_to_target_improvement() -> None:
    claim = _load("cara_claim.json")
    time_claim = claim["time_to_target_claim"]
    assert isinstance(time_claim, dict)
    time_claim["candidate_upper"] = 120.0

    report = validate_cara_certificate(claim)

    assert not report.ok
    assert report.predicates["TimeToTargetOK"] is False


def test_raw_net_capital_and_risk_certificate_fail_on_noncompensable_hazard() -> None:
    assert compute_raw_net_capital(10.0, 2.0, 1.0, 0.5) == 6.5
    certificate = _load("risk_ledger.json")
    hazard = certificate["hazard"]
    assert isinstance(hazard, dict)
    hazard["noncompensable_clearance"] = False

    report = validate_risk_certificate(certificate)

    assert not report.ok
    assert report.predicates["NoncompensableHazardOK"] is False


def test_dependency_closure_and_settlement_capital_accounting() -> None:
    closure = validate_dependency_closure(
        [
            {"object_id": "tok-a", "object_type": "Tok", "available": True},
            {"object_id": "ver-a", "object_type": "Ver", "included_in_packet": True},
        ],
        available_objects=[],
    )
    assert closure.ok

    capital = compute_portfolio_capital(
        [
            {"ledger": "settlement", "capital_delta": 2.0},
            {"ledger": "exploration", "capital_delta": 99.0},
        ]
    )
    assert capital == 2.0


def test_reproduction_capacity_and_recombination_fail_closed() -> None:
    assert capacity_capped_growth([[0.5, 0.5]], [4.0, 4.0], [3.0]) == [3.0]
    certificate = _load("reproduction_record.json")
    certificate["recombination"] = {"claimed": True}

    report = validate_reproduction_certificate(certificate)

    assert not report.ok
    assert report.predicates["RecombinationIdentified"] is False


def test_statistical_bounds_are_reproducible_and_selection_adjusted() -> None:
    adjusted = post_selection_adjusted_confidence(0.95, selected_from=5)
    lower = empirical_bernstein_lower_bound([0.4, 0.6, 0.7, 0.9], 0.0, 1.0, adjusted)
    report = bounded_mean_report([0.4, 0.6, 0.7, 0.9], 0.0, 1.0, 0.95, selected_from=5)

    assert adjusted > 0.95
    assert lower < 0.65
    assert report.ok
    assert report.metrics["n"] == 4

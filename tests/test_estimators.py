from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from alt_foundry_kernel import load_schema
from alt_foundry_kernel.estimators import (
    estimate_alpha_budget,
    estimate_cara_time_to_target,
    estimate_causal_effect,
    estimate_certificate,
    estimate_finite_sample,
    estimate_transport_diagnostics,
)

ROOT = Path(__file__).resolve().parents[1]
ESTIMATORS = ROOT / "examples" / "estimators"


def _load(name: str) -> dict[str, object]:
    return json.loads((ESTIMATORS / name).read_text(encoding="utf-8"))


def test_all_estimator_examples_emit_ok_certificate_reports() -> None:
    report_validator = Draft202012Validator(load_schema("certificate-report"))
    for path in sorted(ESTIMATORS.glob("*.json")):
        report = estimate_certificate(path.stem.replace("_", "-"), json.loads(path.read_text()))

        assert report.ok, path.name
        assert "certificate" in report.artifacts, path.name
        report_validator.validate(report.model_dump(mode="json"))


def test_finite_sample_estimator_is_deterministic_and_selection_adjusted() -> None:
    report = estimate_finite_sample(_load("finite_sample.json"))

    assert report.ok
    assert report.metrics["n"] == 30
    assert report.metrics["adjusted_confidence"] > 0.9
    assert report.metrics["empirical_bernstein_lower"] > 0


def test_causal_estimator_fails_without_overlap_or_identification() -> None:
    no_overlap = {
        "mode": "off_policy",
        "identification": {"status": "valid"},
        "records": [{"reward": 1.0, "target_prob": 1.0, "logging_prob": 0.0}],
    }
    no_identification = _load("causal_effect.json")
    identification = no_identification["identification"]
    assert isinstance(identification, dict)
    identification["status"] = "missing"

    assert not estimate_causal_effect(no_overlap).ok
    assert not estimate_causal_effect(no_identification).ok


def test_transport_estimator_fails_on_uncovered_or_high_dimensional_target() -> None:
    payload = _load("transport_diagnostics.json")
    payload["target_points"] = [[10.0, 10.0]]

    report = estimate_transport_diagnostics(payload)

    assert not report.ok
    assert report.predicates["SupportCoverageOK"] is False
    assert report.predicates["WassersteinRadiusOK"] is False


def test_cara_estimator_requires_safe_time_to_target_margin() -> None:
    payload = _load("cara_time_to_target.json")
    payload["candidate_path"] = [1.0, 2.0, 3.0]

    report = estimate_cara_time_to_target(payload)

    assert not report.ok
    assert report.predicates["TimeToTargetImprovementOK"] is False


def test_alpha_budget_blocks_exhausted_settlement_budget() -> None:
    payload = _load("alpha_budget.json")
    payload["alpha_requested"] = 0.04

    report = estimate_alpha_budget(payload)

    assert not report.ok
    assert report.predicates["AlphaBudgetOK"] is False

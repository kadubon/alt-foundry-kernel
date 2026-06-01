"""Causal and counterfactual certificate checks for ALT packets."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import EstimandType, IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at

CAUSAL_EVIDENCE_MODES = {
    "randomized",
    "paired",
    "replay",
    "off_policy",
    "doubly_robust",
}


def validate_causal_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate a declared potential-outcome or calibrated-proxy certificate.

    This checker verifies certificate structure and fail-closed gates. It does not
    infer identification from observational data by itself.
    """

    report = CertificateReport(
        name="causal",
        claim="counterfactual effect and baseline certificate",
        level="settlement",
    )
    estimand_type = value_at(certificate, "estimand.estimand_type")
    evidence_mode = value_at(certificate, "evidence.mode")
    effect_lower = numeric(certificate, "effect.lower_bound")

    required = (
        "estimand.estimand_type",
        "baseline.status",
        "baseline.comparator_id",
        "identification.status",
        "effect.lower_bound",
        "effect.unit",
        "evidence.mode",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Causal certification requires this field.",
            )

    report.require(
        "BaselineComparatorOK",
        status_is(certificate, "baseline.status", "valid", "live"),
        "baseline.status",
        "A resource-matched live or valid baseline is required.",
    )
    report.require(
        "IdentificationOK",
        status_is(certificate, "identification.status", "valid"),
        "identification.status",
        "Identification assumptions must be explicitly valid.",
    )
    report.require(
        "EffectLowerBoundOK",
        effect_lower is not None,
        "effect.lower_bound",
        "Effect lower bound must be numeric and explicit.",
    )

    if estimand_type == EstimandType.PROXY_ONLY.value:
        report.predicates["SettlementGrade"] = False
        report.add_issue(
            IssueSeverity.INFO,
            "proxy-only-exploration",
            "estimand.estimand_type",
            "Proxy-only evidence is not settlement-grade capital evidence.",
        )
    elif estimand_type == EstimandType.CALIBRATED_PROXY.value:
        report.require(
            "CalibrationBridgeOK",
            status_is(certificate, "calibration.status", "valid"),
            "calibration.status",
            "Calibrated proxy evidence requires an explicit valid calibration bridge.",
        )
        report.predicates["SettlementGrade"] = True
    elif estimand_type == EstimandType.CAUSAL.value:
        report.require(
            "CausalModeOK",
            evidence_mode in CAUSAL_EVIDENCE_MODES,
            "evidence.mode",
            "Causal estimands require a recognized evidence mode.",
        )
        report.predicates["SettlementGrade"] = True
    else:
        report.predicates["SettlementGrade"] = False
        report.add_issue(
            IssueSeverity.ERROR,
            "estimand-not-supported",
            "estimand.estimand_type",
            "Unknown estimand type.",
        )

    mode_required = _required_for_mode(str(evidence_mode))
    for path in mode_required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "mode-required-field-missing",
                path,
                f"Evidence mode {evidence_mode!r} requires this field.",
            )

    report.metrics["effect_lower_bound"] = effect_lower
    report.metrics["positive_effect"] = effect_lower is not None and effect_lower > 0
    return report


def _required_for_mode(mode: str) -> tuple[str, ...]:
    if mode == "randomized":
        return ("evidence.randomization_unit", "evidence.assignment_record")
    if mode == "paired":
        return ("evidence.pairing_key", "evidence.balance_report")
    if mode == "replay":
        return ("evidence.replay_protocol", "evidence.counterfactual_baseline_trace")
    if mode == "off_policy":
        return ("evidence.logging_policy", "evidence.target_policy", "evidence.overlap_report")
    if mode == "doubly_robust":
        return (
            "evidence.logging_policy",
            "evidence.outcome_model",
            "evidence.propensity_model",
            "evidence.overlap_report",
        )
    return ()

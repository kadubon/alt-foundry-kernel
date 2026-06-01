"""CARA target-crossing certificate checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at

CARA_REQUIRED_WHEN_CLAIMED = (
    "asi_target_id",
    "capability_basis_id",
    "target_validity_certificate.status",
    "baseline_upper_envelope.status",
    "target_membership_proof.status",
    "viability_witness.status",
    "time_to_target_claim.baseline_upper",
    "time_to_target_claim.candidate_upper",
)


def validate_cara_certificate(claim: Mapping[str, Any]) -> CertificateReport:
    """Validate conditional target-crossing and time-to-target claims."""

    report = CertificateReport(
        name="cara",
        claim="capability acceleration and target-crossing certificate",
        level="settlement",
    )
    target_claimed = value_at(claim, "claims_target_crossing") is True
    time_claimed = target_claimed or value_at(claim, "claims_time_to_target_comparison") is True
    report.predicates["TargetClaimed"] = target_claimed
    report.predicates["TimeToTargetClaimed"] = time_claimed
    if not target_claimed and not time_claimed:
        report.predicates["TargetValidityOK"] = None
        report.predicates["BaselineEnvelopeOK"] = None
        return report

    for path in CARA_REQUIRED_WHEN_CLAIMED:
        if not present(claim, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "cara-required-field-missing",
                path,
                "Target-crossing or time-to-target claims require this field.",
            )

    target_ok = status_is(claim, "target_validity_certificate.status", "valid") and status_is(
        claim, "target_membership_proof.status", "valid"
    )
    baseline_ok = status_is(claim, "baseline_upper_envelope.status", "valid")
    viability_ok = status_is(claim, "viability_witness.status", "valid")
    baseline_upper = numeric(claim, "time_to_target_claim.baseline_upper")
    candidate_upper = numeric(claim, "time_to_target_claim.candidate_upper")
    acceleration = None
    if baseline_upper is not None and candidate_upper is not None:
        acceleration = baseline_upper - candidate_upper

    report.require(
        "TargetValidityOK",
        target_ok,
        "target_validity_certificate.status",
        "Target validity and target membership must both be valid.",
    )
    report.require(
        "BaselineEnvelopeOK",
        baseline_ok,
        "baseline_upper_envelope.status",
        "Baseline upper envelope must be valid for time-to-target comparisons.",
    )
    report.require(
        "ViabilityOK",
        viability_ok,
        "viability_witness.status",
        "Target crossing must have a valid viability witness.",
    )
    report.require(
        "TimeToTargetOK",
        acceleration is not None and acceleration > 0,
        "time_to_target_claim",
        "Candidate upper time-to-target must improve on the baseline upper envelope.",
    )
    report.metrics.update(
        {
            "baseline_time_to_target_upper": baseline_upper,
            "candidate_time_to_target_upper": candidate_upper,
            "time_to_target_acceleration_lower": acceleration,
        }
    )
    return report

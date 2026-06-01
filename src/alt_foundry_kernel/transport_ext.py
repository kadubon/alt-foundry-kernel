"""Extended transport robustness checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is


def validate_transport_robustness(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate robust estimated transport and causal-invariance guards."""

    report = CertificateReport(
        name="transport_ext",
        claim="robust transportability certificate",
        level="settlement",
    )
    required = (
        "support.status",
        "robust_estimate.status",
        "wasserstein.radius_upper_bound",
        "wasserstein.radius_threshold",
        "causal_invariance.status",
        "observable_stopping.status",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Robust transport certification requires this field.",
            )

    radius = numeric(certificate, "wasserstein.radius_upper_bound")
    threshold = numeric(certificate, "wasserstein.radius_threshold")
    report.require(
        "SupportCoverageOK",
        status_is(certificate, "support.status", "covered", "valid"),
        "support.status",
        "Transport requires support coverage.",
    )
    report.require(
        "RobustEstimateOK",
        status_is(certificate, "robust_estimate.status", "valid"),
        "robust_estimate.status",
        "Estimated transport must include a valid robust certificate.",
    )
    report.require(
        "WassersteinRadiusOK",
        radius is not None and threshold is not None and radius <= threshold,
        "wasserstein.radius_upper_bound",
        "Finite-sample transport radius must be within the declared threshold.",
    )
    report.require(
        "CausalInvarianceOK",
        status_is(certificate, "causal_invariance.status", "valid", "not_required"),
        "causal_invariance.status",
        "Causal-invariance transport evidence must be valid or not required.",
    )
    report.require(
        "ObservableStoppingOK",
        status_is(certificate, "observable_stopping.status", "valid"),
        "observable_stopping.status",
        "Transport-validity stopping rule must be observable and valid.",
    )
    report.metrics["wasserstein_radius_upper_bound"] = radius
    report.metrics["wasserstein_radius_threshold"] = threshold
    return report

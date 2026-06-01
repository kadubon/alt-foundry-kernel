"""Transportability and context-refresh checks for ALT certificates."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is


def validate_transport_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate support, density-ratio, drift, and refresh transport records."""

    report = CertificateReport(
        name="transport",
        claim="context transport and opportunity-law refresh certificate",
        level="settlement",
    )
    required = (
        "source_context",
        "target_context",
        "support.status",
        "support.overlap_min",
        "density_ratio.upper_bound",
        "drift.status",
        "refresh.status",
        "transport_cost.upper_bound",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Transport certification requires this field.",
            )

    overlap_min = numeric(certificate, "support.overlap_min")
    ratio_upper = numeric(certificate, "density_ratio.upper_bound")
    cost_upper = numeric(certificate, "transport_cost.upper_bound")

    report.require(
        "SupportCovered",
        status_is(certificate, "support.status", "covered", "valid")
        and overlap_min is not None
        and overlap_min > 0,
        "support",
        "Target context must be covered by declared source support.",
    )
    report.require(
        "DensityRatioBounded",
        ratio_upper is not None and ratio_upper >= 1,
        "density_ratio.upper_bound",
        "Density-ratio upper bound must be finite and at least one.",
    )
    report.require(
        "DriftOK",
        status_is(certificate, "drift.status", "stable", "valid", "charged"),
        "drift.status",
        "Drift must be stable, valid, or explicitly charged.",
    )
    report.require(
        "RefreshOK",
        status_is(certificate, "refresh.status", "valid", "not_required"),
        "refresh.status",
        "Baseline and opportunity-law refresh status must be valid or not required.",
    )
    report.require(
        "TransportCostBounded",
        cost_upper is not None and cost_upper >= 0,
        "transport_cost.upper_bound",
        "Transport cost upper bound must be a non-negative number.",
    )
    report.metrics.update(
        {
            "overlap_min": overlap_min,
            "density_ratio_upper_bound": ratio_upper,
            "transport_cost_upper_bound": cost_upper,
        }
    )
    return report

"""Non-reduction guards for ALT liquidity claims."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, present, status_is, value_at

NON_REDUCTION_SHORTCUTS = {
    "compression",
    "novelty",
    "benchmark_score",
    "transfer_score",
    "trace_volume",
    "library_size",
    "duplicate_count",
    "static_surplus_only",
    "evidence_volume",
    "surface_packaging",
    "category_structure",
    "generality",
}


def validate_non_reduction_audit(audit: Mapping[str, Any]) -> CertificateReport:
    """Reject common shortcuts that the paper proves do not imply liquidity."""

    report = CertificateReport(
        name="non_reduction",
        claim="ALT non-reduction audit",
        level="audit",
    )
    required = (
        "liquidity_claim.status",
        "measurement.status",
        "signed_surplus.status",
        "transport.status",
        "hazard.status",
        "authority.status",
        "lifecycle.status",
        "finality.status",
    )
    for path in required:
        if not present(audit, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Non-reduction audit requires this field.",
            )

    report.require(
        "LiquidityClaimExplicit",
        status_is(audit, "liquidity_claim.status", "explicit", "valid"),
        "liquidity_claim.status",
        "Liquidity claim must be explicit, not inferred from a proxy property.",
    )
    for predicate, path in (
        ("MeasurementPresent", "measurement.status"),
        ("SignedSurplusPresent", "signed_surplus.status"),
        ("TransportPresent", "transport.status"),
        ("HazardPresent", "hazard.status"),
        ("AuthorityPresent", "authority.status"),
        ("LifecyclePresent", "lifecycle.status"),
        ("FinalityPresent", "finality.status"),
    ):
        report.require(
            predicate,
            status_is(audit, path, "valid", "present", "bounded", "finalized"),
            path,
            f"{predicate} must be declared for liquidity certification.",
        )

    shortcuts = value_at(audit, "shortcuts")
    violating: list[str] = []
    if isinstance(shortcuts, list):
        for item in shortcuts:
            if not isinstance(item, Mapping):
                continue
            name = item.get("name")
            if (
                isinstance(name, str)
                and name in NON_REDUCTION_SHORTCUTS
                and item.get("used_as_certification") is True
            ):
                violating.append(name)
    report.predicates["ShortcutFree"] = not violating
    report.artifacts["violating_shortcuts"] = violating
    if violating:
        report.add_issue(
            IssueSeverity.ERROR,
            "non-reduction-shortcut",
            "shortcuts",
            "ALT liquidity cannot be certified from non-reduction shortcut properties.",
        )

    if value_at(audit, "capital_effect.claims_settlement") is True:
        report.require(
            "KernelRouteDeclared",
            status_is(audit, "kernel_route.status", "valid"),
            "kernel_route.status",
            "Capital-changing claims must route through the executable kernel.",
        )
    return report

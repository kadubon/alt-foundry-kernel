"""Certificate algebra and composition guards."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, present, status_is, value_at


def validate_certificate_composition(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate common-estimand composition and negative-scope propagation."""

    report = CertificateReport(
        name="certificate_algebra",
        claim="certificate composition certificate",
        level="audit",
    )
    required = ("operation", "certificates", "composition.naive", "common_estimand.status")
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Certificate algebra requires this field.",
            )

    certificates = certificate.get("certificates")
    estimands: set[str] = set()
    if isinstance(certificates, list):
        for item in certificates:
            if isinstance(item, Mapping) and isinstance(item.get("estimand_id"), str):
                estimands.add(str(item["estimand_id"]))

    operation = value_at(certificate, "operation")
    naive = value_at(certificate, "composition.naive") is True
    common_estimand_ok = (
        status_is(certificate, "common_estimand.status", "valid") and len(estimands) == 1
    )
    report.require(
        "NaiveCompositionRejected",
        not naive,
        "composition.naive",
        "Naive certificate composition is invalid without explicit common-estimand proof.",
    )
    report.require(
        "CommonEstimandOK",
        common_estimand_ok,
        "common_estimand.status",
        "Composition requires valid common-estimand evidence.",
    )
    if operation == "negative_propagation":
        report.require(
            "NegativeScopePropagationOK",
            status_is(certificate, "negative_scope.status", "valid"),
            "negative_scope.status",
            "Negative certificates require scope-safe propagation evidence.",
        )
    else:
        report.predicates["NegativeScopePropagationOK"] = None
    report.metrics["certificate_count"] = len(certificates) if isinstance(certificates, list) else 0
    report.artifacts["estimand_ids"] = sorted(estimands)
    return report

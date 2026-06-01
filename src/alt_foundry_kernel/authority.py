"""Authority, capability, threat, runtime-witness, and telemetry checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, present, status_is, value_at


def validate_authority_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate guarded-deployment controls for a token claim."""

    report = CertificateReport(
        name="authority",
        claim="authority/capability/threat guarded deployment certificate",
        level="settlement",
    )
    required = (
        "authority.status",
        "capability.status",
        "threat_model.status",
        "runtime_witness.status",
        "telemetry.status",
        "guard.status",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Guarded deployment certification requires this field.",
            )

    telemetry_valid = status_is(certificate, "telemetry.status", "valid") or (
        value_at(certificate, "telemetry.worst_case_charge_applied") is True
    )
    report.require(
        "AuthorityOK",
        status_is(certificate, "authority.status", "valid"),
        "authority.status",
        "Authority envelope must be valid.",
    )
    report.require(
        "CapabilityOK",
        status_is(certificate, "capability.status", "valid"),
        "capability.status",
        "Capability envelope must be valid.",
    )
    report.require(
        "ThreatOK",
        status_is(certificate, "threat_model.status", "cleared"),
        "threat_model.status",
        "Adversarial token threat model must be cleared.",
    )
    report.require(
        "RuntimeWitnessOK",
        status_is(certificate, "runtime_witness.status", "valid"),
        "runtime_witness.status",
        "Runtime capital witness must be valid.",
    )
    report.require(
        "TelemetryOK",
        telemetry_valid,
        "telemetry.status",
        "Telemetry must be valid or a worst-case charge must be applied.",
    )
    report.require(
        "GuardOK",
        status_is(certificate, "guard.status", "valid", "confined"),
        "guard.status",
        "Guarded deployment policy must be valid or confined.",
    )
    return report

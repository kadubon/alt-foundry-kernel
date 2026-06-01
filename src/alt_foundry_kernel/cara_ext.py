"""Extended target-valid ALT-CARA process checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at


def validate_cara_process(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate target-valid ALT-CARA process guardrails."""

    report = CertificateReport(
        name="cara_ext",
        claim="target-valid ALT-CARA process certificate",
        level="settlement",
    )
    required = (
        "target.status",
        "non_tradable_constraints.satisfied",
        "baseline_upper_envelope.status",
        "capability_process.status",
        "viability_control.status",
        "raw_net_capital.lower_bound",
        "time_to_target.acceleration_lower_bound",
        "stopping_conditions.status",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "ALT-CARA process certification requires this field.",
            )

    raw_net = numeric(certificate, "raw_net_capital.lower_bound")
    acceleration = numeric(certificate, "time_to_target.acceleration_lower_bound")
    report.require(
        "TargetValidityOK",
        status_is(certificate, "target.status", "valid"),
        "target.status",
        "Declared ASI target must have a valid target certificate.",
    )
    report.require(
        "NonTradableConstraintsOK",
        value_at(certificate, "non_tradable_constraints.satisfied") is True,
        "non_tradable_constraints.satisfied",
        "Non-tradable target constraints cannot be offset by surplus.",
    )
    report.require(
        "BaselineUpperEnvelopeOK",
        status_is(certificate, "baseline_upper_envelope.status", "valid"),
        "baseline_upper_envelope.status",
        "Baseline upper-envelope certificate must be valid.",
    )
    report.require(
        "CapabilityProcessOK",
        status_is(certificate, "capability_process.status", "valid"),
        "capability_process.status",
        "Certified capability-capital process must be valid.",
    )
    report.require(
        "ViabilityControlledOK",
        status_is(certificate, "viability_control.status", "valid"),
        "viability_control.status",
        "ASI-relevant acceleration must be viability-controlled.",
    )
    report.require(
        "RawNetSolvencyOK",
        raw_net is not None and raw_net > 0,
        "raw_net_capital.lower_bound",
        "ALT-CARA process must be raw-net solvent.",
    )
    report.require(
        "TimeToTargetImprovementOK",
        acceleration is not None and acceleration > 0,
        "time_to_target.acceleration_lower_bound",
        "Target-valid claim requires positive lower-bound time-to-target improvement.",
    )
    report.require(
        "StoppingConditionsOK",
        status_is(certificate, "stopping_conditions.status", "valid"),
        "stopping_conditions.status",
        "Stopping conditions must be declared and valid.",
    )
    report.metrics["raw_net_capital_lower_bound"] = raw_net
    report.metrics["time_to_target_acceleration_lower_bound"] = acceleration
    return report

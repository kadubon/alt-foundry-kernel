"""Risk, hazard, reserve, and raw-net capital accounting."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is


def compute_raw_net_capital(
    capital_lower_bound: float,
    reserve_upper_bound: float,
    hazard_upper_bound: float,
    irreversible_loss_upper_bound: float = 0.0,
) -> float:
    """Compute conservative raw-net safe certified capital."""

    return (
        capital_lower_bound
        - reserve_upper_bound
        - hazard_upper_bound
        - irreversible_loss_upper_bound
    )


def validate_risk_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate hazard envelopes and raw-net solvency gates."""

    report = CertificateReport(
        name="risk",
        claim="hazard envelope and raw-net solvency certificate",
        level="settlement",
    )
    required = (
        "capital.lower_bound",
        "reserve.upper_bound",
        "hazard.status",
        "hazard.upper_bound",
        "hazard.noncompensable_clearance",
        "irreversible_loss.upper_bound",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Risk certification requires this field.",
            )

    capital = numeric(certificate, "capital.lower_bound")
    reserve = numeric(certificate, "reserve.upper_bound")
    hazard = numeric(certificate, "hazard.upper_bound")
    irreversible = numeric(certificate, "irreversible_loss.upper_bound")
    raw_net = None
    if (
        capital is not None
        and reserve is not None
        and hazard is not None
        and irreversible is not None
    ):
        raw_net = compute_raw_net_capital(capital, reserve, hazard, irreversible)

    report.require(
        "HazardEnvelopeOK",
        status_is(certificate, "hazard.status", "valid", "bounded"),
        "hazard.status",
        "Hazard envelope must be valid or explicitly bounded.",
    )
    report.require(
        "NoncompensableHazardOK",
        certificate.get("hazard", {}).get("noncompensable_clearance") is True
        if isinstance(certificate.get("hazard"), Mapping)
        else False,
        "hazard.noncompensable_clearance",
        "Noncompensable hazards must be cleared, not offset by value.",
    )
    report.require(
        "RawNetSolvencyOK",
        raw_net is not None and raw_net > 0,
        "capital.lower_bound",
        "Raw-net safe certified capital must remain positive after reserves and hazards.",
    )
    report.metrics.update(
        {
            "capital_lower_bound": capital,
            "reserve_upper_bound": reserve,
            "hazard_upper_bound": hazard,
            "irreversible_loss_upper_bound": irreversible,
            "raw_net_capital_lower_bound": raw_net,
        }
    )
    return report

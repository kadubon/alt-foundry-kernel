"""Federated finality and proof-of-useful-abstraction ledger checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at


def validate_finality_poua_ledger(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate finality-safe settlement and PoUA non-authority constraints."""

    report = CertificateReport(
        name="finality",
        claim="federated finality and PoUA ledger certificate",
        level="settlement",
    )
    required = (
        "federated_finality.state",
        "root.status",
        "quorum.threshold",
        "quorum.signed_weight",
        "poua_ledger.status",
        "settlement.finality_safe",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Finality/PoUA certification requires this field.",
            )

    threshold = numeric(certificate, "quorum.threshold")
    signed_weight = numeric(certificate, "quorum.signed_weight")
    quorum_ok = (
        threshold is not None
        and signed_weight is not None
        and threshold > 0
        and signed_weight >= threshold
    )
    report.require(
        "FederatedFinalityOK",
        status_is(certificate, "federated_finality.state", "finalized"),
        "federated_finality.state",
        "Federated finality state must be finalized for settlement.",
    )
    report.require(
        "RootOK",
        status_is(certificate, "root.status", "valid"),
        "root.status",
        "Root status must be valid.",
    )
    report.require(
        "WeightedQuorumOK",
        quorum_ok,
        "quorum.signed_weight",
        "Signed PoUA/root quorum weight must meet the declared threshold.",
    )
    report.require(
        "PoUANotEpistemicAuthority",
        value_at(certificate, "poua_ledger.used_as_epistemic_authority") is not True,
        "poua_ledger.used_as_epistemic_authority",
        "PoUA weight cannot replace epistemic evidence or evaluator independence.",
    )
    report.require(
        "FinalitySafeSettlement",
        value_at(certificate, "settlement.finality_safe") is True,
        "settlement.finality_safe",
        "Settlement must be marked finality-safe.",
    )
    report.metrics["quorum_threshold"] = threshold
    report.metrics["signed_weight"] = signed_weight
    return report

"""Liquidity reproduction, capacity, and recombination certificate helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at


def capacity_capped_growth(
    reproduction_matrix: Sequence[Sequence[float]],
    state_vector: Sequence[float],
    capacity_vector: Sequence[float],
) -> list[float]:
    """Apply a non-negative multitype reproduction matrix with capacity caps."""

    matrix = np.asarray(reproduction_matrix, dtype=float)
    state = np.asarray(state_vector, dtype=float)
    capacity = np.asarray(capacity_vector, dtype=float)
    if matrix.ndim != 2 or state.ndim != 1 or capacity.ndim != 1:
        raise ValueError("matrix must be 2-D and vectors must be 1-D")
    if matrix.shape[1] != state.shape[0] or matrix.shape[0] != capacity.shape[0]:
        raise ValueError("matrix and vector dimensions are incompatible")
    if np.any(matrix < 0) or np.any(state < 0) or np.any(capacity < 0):
        raise ValueError("reproduction inputs must be non-negative")
    growth = matrix @ state
    return [float(item) for item in np.minimum(growth, capacity)]


def validate_reproduction_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate reproduction matrix and recombination claims.

    Recombination tensor estimation remains fail-closed unless the certificate
    supplies an explicit valid identification record.
    """

    report = CertificateReport(
        name="reproduction",
        claim="liquidity reproduction and recombination certificate",
        level="evidence",
    )
    required = (
        "matrix.status",
        "matrix.values",
        "gauge.status",
        "capacity.status",
        "identification.status",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Reproduction certification requires this field.",
            )

    report.require(
        "MatrixOK",
        status_is(certificate, "matrix.status", "valid"),
        "matrix.status",
        "Reproduction matrix must be explicitly valid.",
    )
    report.require(
        "GaugeOK",
        status_is(certificate, "gauge.status", "valid"),
        "gauge.status",
        "Valuation gauge and aggregation map must be valid.",
    )
    report.require(
        "CapacityOK",
        status_is(certificate, "capacity.status", "valid"),
        "capacity.status",
        "Receiver or foundry capacity must be valid.",
    )
    report.require(
        "IdentificationOK",
        status_is(certificate, "identification.status", "valid"),
        "identification.status",
        "Causal reproduction identification must be explicit.",
    )

    recombination_claimed = value_at(certificate, "recombination.claimed") is True
    report.predicates["RecombinationIdentified"] = (
        status_is(certificate, "recombination.identification_status", "valid")
        if recombination_claimed
        else None
    )
    if recombination_claimed and report.predicates["RecombinationIdentified"] is not True:
        report.add_issue(
            IssueSeverity.ERROR,
            "recombination-identification-missing",
            "recombination.identification_status",
            "Recombination claims fail closed without valid tensor identification.",
        )

    spectral_radius = numeric(certificate, "matrix.spectral_radius")
    if spectral_radius is not None:
        report.metrics["spectral_radius"] = spectral_radius
        report.predicates["NonExplosiveGrowthBounded"] = spectral_radius < 1 or status_is(
            certificate, "capacity.status", "valid"
        )
    return report

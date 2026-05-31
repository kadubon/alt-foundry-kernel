"""Signed-bound accounting for ALT surplus claims."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.models import SignedBoundReport

LOWER_FIELDS = (
    "value_lower_bound",
    "cost_upper_bound",
    "risk_upper_bound",
    "transport_upper_bound",
)
UPPER_FIELDS = (
    "value_upper_bound",
    "cost_lower_bound",
    "risk_lower_bound",
    "transport_lower_bound",
)


def _number(bounds: Mapping[str, Any], key: str) -> float | None:
    value = bounds.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def compute_signed_bounds(bounds: Mapping[str, Any]) -> SignedBoundReport:
    """Compute conservative surplus lower/upper bounds.

    ALT's sign discipline uses lower value minus upper costs for positive settlement,
    and upper value minus lower costs for negative-liquidity pruning.
    """

    missing_lower = [field for field in LOWER_FIELDS if _number(bounds, field) is None]
    lower = None
    if not missing_lower:
        lower = (
            float(bounds["value_lower_bound"])
            - float(bounds["cost_upper_bound"])
            - float(bounds["risk_upper_bound"])
            - float(bounds["transport_upper_bound"])
        )

    missing_upper = [field for field in UPPER_FIELDS if _number(bounds, field) is None]
    upper = None
    if not missing_upper:
        upper = (
            float(bounds["value_upper_bound"])
            - float(bounds["cost_lower_bound"])
            - float(bounds["risk_lower_bound"])
            - float(bounds["transport_lower_bound"])
        )

    return SignedBoundReport(
        lower_bound=lower,
        upper_bound=upper,
        missing_for_lower=missing_lower,
        missing_for_upper=missing_upper,
    )

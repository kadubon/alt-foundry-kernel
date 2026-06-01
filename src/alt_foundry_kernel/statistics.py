"""Reproducible statistical bound helpers for ALT certificates."""

from __future__ import annotations

from collections.abc import Sequence
from math import log, sqrt

import numpy as np
from scipy import stats

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport


def mean_confidence_interval(
    values: Sequence[float], confidence: float = 0.95
) -> tuple[float, float, float]:
    """Return mean and two-sided Student-t confidence interval."""

    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("values must not be empty")
    mean = float(np.mean(arr))
    if arr.size == 1:
        return mean, mean, mean
    sem = float(stats.sem(arr))
    margin = float(stats.t.ppf((1.0 + confidence) / 2.0, arr.size - 1) * sem)
    return mean, mean - margin, mean + margin


def empirical_bernstein_lower_bound(
    values: Sequence[float],
    lower: float,
    upper: float,
    confidence: float = 0.95,
) -> float:
    """Compute a conservative empirical-Bernstein lower mean bound."""

    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError("values must not be empty")
    if upper <= lower:
        raise ValueError("upper must be greater than lower")
    if np.any(arr < lower) or np.any(arr > upper):
        raise ValueError("all values must lie inside [lower, upper]")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")

    n = arr.size
    delta = 1.0 - confidence
    variance = float(np.var(arr, ddof=1)) if n > 1 else 0.0
    radius = sqrt(2.0 * variance * log(3.0 / delta) / n) + (
        3.0 * (upper - lower) * log(3.0 / delta) / n
    )
    return float(np.mean(arr) - radius)


def post_selection_adjusted_confidence(
    confidence: float, selected_from: int, minimum_delta: float = 1e-12
) -> float:
    """Bonferroni-style confidence adjustment for selected certificates."""

    if selected_from < 1:
        raise ValueError("selected_from must be positive")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0, 1)")
    delta = max((1.0 - confidence) / selected_from, minimum_delta)
    return 1.0 - delta


def bounded_mean_report(
    values: Sequence[float],
    lower: float,
    upper: float,
    confidence: float = 0.95,
    selected_from: int = 1,
) -> CertificateReport:
    """Build a language-neutral report for bounded empirical value evidence."""

    report = CertificateReport(name="statistics", claim="bounded empirical mean", level="evidence")
    try:
        adjusted = post_selection_adjusted_confidence(confidence, selected_from)
        mean, ci_lower, ci_upper = mean_confidence_interval(values, adjusted)
        eb_lower = empirical_bernstein_lower_bound(values, lower, upper, adjusted)
    except ValueError as exc:
        report.add_issue(IssueSeverity.ERROR, "statistical-input-invalid", "<root>", str(exc))
        return report

    report.predicates.update(
        {
            "BoundsDeclared": True,
            "FiniteSampleOK": len(values) > 0,
            "PostSelectionAdjusted": selected_from >= 1,
        }
    )
    report.metrics.update(
        {
            "n": len(values),
            "mean": mean,
            "confidence": confidence,
            "adjusted_confidence": adjusted,
            "t_lower": ci_lower,
            "t_upper": ci_upper,
            "empirical_bernstein_lower": eb_lower,
        }
    )
    return report

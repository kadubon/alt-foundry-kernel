"""Sequential evidence and settle-or-sample decision checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, value_at


def validate_sequential_decision(decision: Mapping[str, Any]) -> CertificateReport:
    """Validate adaptive horizon, EVSI, and finite evidence-budget gates."""

    report = CertificateReport(
        name="sequential",
        claim="sequential settle-or-sample decision certificate",
        level="evidence",
    )
    required = (
        "decision",
        "horizon.remaining",
        "surplus.lower_bound",
        "sampling.cost_upper_bound",
        "sampling.evsi_lower_bound",
        "budget.remaining",
        "budget.max_sampling_cost",
    )
    for path in required:
        if not present(decision, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Sequential evidence decision requires this field.",
            )

    action = value_at(decision, "decision")
    horizon = numeric(decision, "horizon.remaining")
    surplus = numeric(decision, "surplus.lower_bound")
    sample_cost = numeric(decision, "sampling.cost_upper_bound")
    evsi = numeric(decision, "sampling.evsi_lower_bound")
    budget_remaining = numeric(decision, "budget.remaining")
    max_sampling_cost = numeric(decision, "budget.max_sampling_cost")

    finite_budget = (
        budget_remaining is not None
        and max_sampling_cost is not None
        and budget_remaining >= 0
        and max_sampling_cost >= 0
    )
    sample_affordable = (
        finite_budget
        and sample_cost is not None
        and budget_remaining is not None
        and sample_cost <= budget_remaining
    )
    settle_ok = action == "settle" and surplus is not None and surplus > 0
    sample_ok = (
        action == "sample"
        and evsi is not None
        and sample_cost is not None
        and evsi > sample_cost
        and sample_affordable
    )
    defer_ok = action == "defer" and horizon is not None and horizon <= 0

    report.require(
        "FiniteEvidenceBudgetOK",
        finite_budget,
        "budget",
        "Sequential evidence control requires a finite evidence budget.",
    )
    report.require(
        "HorizonOK",
        horizon is not None and horizon >= 0,
        "horizon.remaining",
        "Remaining horizon must be non-negative.",
    )
    report.require(
        "SettleOrSampleOK",
        settle_ok or sample_ok or defer_ok,
        "decision",
        "Decision must be justified by positive surplus, "
        "positive EVSI net of cost, or exhausted horizon.",
    )
    report.metrics.update(
        {
            "horizon_remaining": horizon,
            "surplus_lower_bound": surplus,
            "sample_cost_upper_bound": sample_cost,
            "evsi_lower_bound": evsi,
            "budget_remaining": budget_remaining,
        }
    )
    return report

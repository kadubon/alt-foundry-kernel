"""Foundry control, bottleneck, and conservative exploration checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is


def validate_foundry_control_state(state: Mapping[str, Any]) -> CertificateReport:
    """Validate bottleneck, shadow-price, capacity, and exploration controls."""

    report = CertificateReport(
        name="foundry_control",
        claim="foundry control and conservative exploration certificate",
        level="audit",
    )
    required = (
        "bottleneck.min_cut_capacity",
        "bottleneck.demand_upper_bound",
        "shadow_price.status",
        "absorption.capacity_lower_bound",
        "exploration.capital_at_risk_upper_bound",
        "exploration.risk_budget",
        "phase.status",
        "conservative_exploration.status",
    )
    for path in required:
        if not present(state, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Foundry control certification requires this field.",
            )

    min_cut = numeric(state, "bottleneck.min_cut_capacity")
    demand = numeric(state, "bottleneck.demand_upper_bound")
    absorption = numeric(state, "absorption.capacity_lower_bound")
    capital_at_risk = numeric(state, "exploration.capital_at_risk_upper_bound")
    risk_budget = numeric(state, "exploration.risk_budget")
    report.require(
        "BottleneckCapacityOK",
        min_cut is not None and demand is not None and min_cut >= demand,
        "bottleneck",
        "Foundry min-cut throughput must cover declared demand.",
    )
    report.require(
        "ShadowPriceOK",
        status_is(state, "shadow_price.status", "valid", "not_required"),
        "shadow_price.status",
        "Bottleneck shadow-price certificate must be valid or not required.",
    )
    report.require(
        "AbsorptionCapacityOK",
        absorption is not None and demand is not None and absorption >= demand,
        "absorption.capacity_lower_bound",
        "Receiver absorption capacity must cover declared demand.",
    )
    report.require(
        "CapitalConservativeExploration",
        capital_at_risk is not None
        and risk_budget is not None
        and capital_at_risk <= risk_budget,
        "exploration.capital_at_risk_upper_bound",
        "Exploration must remain within the declared capital-at-risk budget.",
    )
    report.require(
        "PhaseControlOK",
        status_is(state, "phase.status", "valid"),
        "phase.status",
        "Foundry phase-control record must be valid.",
    )
    report.require(
        "ConservativeExplorationOK",
        status_is(state, "conservative_exploration.status", "valid"),
        "conservative_exploration.status",
        "Conservative exploration guard must be valid.",
    )
    report.metrics.update(
        {
            "min_cut_capacity": min_cut,
            "demand_upper_bound": demand,
            "absorption_capacity_lower_bound": absorption,
            "capital_at_risk_upper_bound": capital_at_risk,
            "risk_budget": risk_budget,
        }
    )
    return report

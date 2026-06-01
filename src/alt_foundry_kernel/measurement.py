"""Measurement-specification checks for ALT evidence claims."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import EstimandType, IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at

SETTLEMENT_GRADE_ESTIMANDS = {EstimandType.CAUSAL.value, EstimandType.CALIBRATED_PROXY.value}


def validate_measurement_spec(spec: Mapping[str, Any]) -> CertificateReport:
    """Validate the paper-facing task/solver/protocol/evidence measurement surface.

    The checker does not infer measurement validity from raw traces. It verifies that
    a packet has explicit trace, sample, instrumentation, firewall, and selection
    records that a settlement kernel can consume without assigning missing evidence
    a zero cost.
    """

    report = CertificateReport(
        name="measurement",
        claim="ALT task/solver/protocol measurement specification",
        level="evidence",
    )

    required = (
        "task.id",
        "solver.id",
        "protocol.id",
        "estimand.estimand_type",
        "trace_view.projection",
        "sample.design",
        "sample.size",
        "instrumentation.status",
        "trace_sufficiency.status",
        "selection.status",
        "firewall.status",
        "contamination.status",
    )
    for path in required:
        if not present(spec, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Measurement certification requires this field.",
            )

    sample_size = numeric(spec, "sample.size")
    report.require(
        "SamplePositive",
        sample_size is not None and sample_size > 0,
        "sample.size",
        "Sample size must be a positive numeric count.",
    )
    report.require(
        "InstrumentationOK",
        status_is(spec, "instrumentation.status", "valid"),
        "instrumentation.status",
        "Instrumentation must be explicitly valid.",
    )
    report.require(
        "TraceSufficiencyOK",
        status_is(spec, "trace_sufficiency.status", "sufficient", "valid"),
        "trace_sufficiency.status",
        "Observed trace projection must be sufficient for the declared estimand.",
    )
    report.require(
        "SelectionOK",
        status_is(spec, "selection.status", "valid", "not_required"),
        "selection.status",
        "Selection effects must be certified or declared not required.",
    )
    report.require(
        "EvaluatorFirewallOK",
        status_is(spec, "firewall.status", "valid", "isolated"),
        "firewall.status",
        "Evaluator firewall must prevent capture or contamination of held-out evidence.",
    )
    report.require(
        "ContaminationOK",
        status_is(spec, "contamination.status", "clear", "bounded"),
        "contamination.status",
        "Contamination must be cleared or charged by a declared bound.",
    )

    estimand = value_at(spec, "estimand.estimand_type")
    report.predicates["SettlementGradeEstimand"] = estimand in SETTLEMENT_GRADE_ESTIMANDS
    report.metrics["sample_size"] = sample_size
    report.artifacts["estimand_type"] = estimand
    if estimand == EstimandType.PROXY_ONLY.value:
        report.add_issue(
            IssueSeverity.INFO,
            "proxy-only-evidence",
            "estimand.estimand_type",
            "Proxy-only measurement may support exploration but not settlement capital.",
        )
    elif estimand not in SETTLEMENT_GRADE_ESTIMANDS:
        report.add_issue(
            IssueSeverity.ERROR,
            "unknown-estimand",
            "estimand.estimand_type",
            "Settlement measurement requires causal or calibrated-proxy estimands.",
        )

    return report

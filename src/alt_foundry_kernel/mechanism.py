"""Mechanism-mediated reuse and self-certification checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, present, status_is, value_at


def validate_mechanism_certificate(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate placebo, ablation, actor-neutrality, and self-certification guards."""

    report = CertificateReport(
        name="mechanism",
        claim="mechanism-mediated reuse certificate",
        level="settlement",
    )
    required = (
        "placebo.status",
        "ablation.status",
        "actor_neutrality.status",
        "evaluator_independence.status",
        "self_certification.status",
        "mechanism_effect.lower_bound",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Mechanism certification requires this field.",
            )

    effect_lower = numeric(certificate, "mechanism_effect.lower_bound")
    report.require(
        "PlaceboControlled",
        status_is(certificate, "placebo.status", "valid"),
        "placebo.status",
        "Reuse certificate requires a valid placebo or null-token control.",
    )
    report.require(
        "AblationOK",
        status_is(certificate, "ablation.status", "valid"),
        "ablation.status",
        "Mechanism-ablation contrast must be valid.",
    )
    report.require(
        "ActorNeutralOK",
        status_is(certificate, "actor_neutrality.status", "valid"),
        "actor_neutrality.status",
        "Token effect must not depend on privileged actor identity.",
    )
    report.require(
        "EvaluatorIndependent",
        status_is(certificate, "evaluator_independence.status", "valid"),
        "evaluator_independence.status",
        "Evaluator must be independent of the token under test.",
    )
    report.require(
        "SelfCertificationFree",
        status_is(certificate, "self_certification.status", "cleared")
        and value_at(certificate, "self_certification.self_certified") is not True,
        "self_certification.status",
        "Self-certified value claims fail closed.",
    )
    report.require(
        "MechanismEffectPositive",
        effect_lower is not None and effect_lower > 0,
        "mechanism_effect.lower_bound",
        "Mechanism-mediated effect lower bound must be positive.",
    )
    report.metrics["mechanism_effect_lower_bound"] = effect_lower
    return report

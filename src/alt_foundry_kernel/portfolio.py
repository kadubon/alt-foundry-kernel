"""Portfolio, dependency-closure, dominance, and capital accounting utilities."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import networkx as nx

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.models import LedgerEntry
from alt_foundry_kernel.reports import CertificateReport, present, value_at


def validate_dependency_closure(
    dependencies: Sequence[Mapping[str, Any]], available_objects: Iterable[str]
) -> CertificateReport:
    """Validate dependency closure for typed ALT dependency objects."""

    available = set(available_objects)
    report = CertificateReport(
        name="portfolio",
        claim="dependency closure and portfolio feasibility",
        level="settlement",
    )
    graph: nx.DiGraph[str] = nx.DiGraph()
    missing: list[str] = []
    for dependency in dependencies:
        object_id = dependency.get("object_id")
        if not isinstance(object_id, str) or not object_id:
            report.add_issue(
                IssueSeverity.ERROR,
                "dependency-id-missing",
                "dependencies",
                "Each dependency must have an object_id.",
            )
            continue
        graph.add_node(object_id)
        parent = dependency.get("depends_on")
        if isinstance(parent, str) and parent:
            graph.add_edge(object_id, parent)
        if (
            object_id not in available
            and dependency.get("available") is not True
            and dependency.get("included_in_packet") is not True
        ):
            missing.append(object_id)

    report.predicates["AcyclicDependencyGraph"] = nx.is_directed_acyclic_graph(graph)
    report.predicates["DependencyClosed"] = not missing
    report.metrics["dependency_count"] = len(dependencies)
    report.artifacts["missing_dependencies"] = missing
    if not nx.is_directed_acyclic_graph(graph):
        report.add_issue(
            IssueSeverity.ERROR,
            "dependency-cycle",
            "dependencies",
            "Dependency graph must be acyclic for deterministic settlement.",
        )
    if missing:
        report.add_issue(
            IssueSeverity.ERROR,
            "dependency-not-available",
            "dependencies",
            "Dependency closure is incomplete.",
        )
    return report


def compute_portfolio_capital(entries: Sequence[LedgerEntry | Mapping[str, Any]]) -> float:
    """Sum settlement-ledger capital deltas only."""

    capital = 0.0
    for entry in entries:
        ledger = entry.ledger if isinstance(entry, LedgerEntry) else entry.get("ledger")
        delta = (
            entry.capital_delta
            if isinstance(entry, LedgerEntry)
            else entry.get("capital_delta", 0.0)
        )
        if (
            ledger == "settlement"
            and isinstance(delta, int | float)
            and not isinstance(delta, bool)
        ):
            capital += float(delta)
    return capital


def validate_dominance_claim(claim: Mapping[str, Any]) -> CertificateReport:
    """Validate a declared deployment-dominance comparison."""

    report = CertificateReport(name="dominance", claim="deployment dominance", level="audit")
    required = (
        "candidate.token_id",
        "incumbent.token_id",
        "candidate.value_lower_bound",
        "candidate.cost_upper_bound",
        "incumbent.value_upper_bound",
        "incumbent.cost_lower_bound",
    )
    for path in required:
        if not present(claim, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Dominance comparison requires this field.",
            )
    candidate_margin = _number(value_at(claim, "candidate.value_lower_bound")) - _number(
        value_at(claim, "candidate.cost_upper_bound")
    )
    incumbent_margin = _number(value_at(claim, "incumbent.value_upper_bound")) - _number(
        value_at(claim, "incumbent.cost_lower_bound")
    )
    dominates = candidate_margin > incumbent_margin
    report.predicates["DominanceOK"] = dominates
    report.metrics.update(
        {"candidate_margin": candidate_margin, "incumbent_margin": incumbent_margin}
    )
    if not dominates:
        report.add_issue(
            IssueSeverity.ERROR,
            "dominance-not-established",
            "<root>",
            "Candidate lower margin does not exceed incumbent upper margin.",
        )
    return report


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return float("-inf")
    return float(value)

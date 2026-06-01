"""Extended portfolio constraints and breadth-gaming guards."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, present, status_is, value_at


def validate_portfolio_constraints(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate conflict constraints, breadth partitions, and cherry-picking guards."""

    report = CertificateReport(
        name="portfolio_ext",
        claim="portfolio conflict and breadth certificate",
        level="settlement",
    )
    required = (
        "tokens",
        "selection",
        "conflicts",
        "breadth_partition.status",
        "cherry_picking.status",
        "behavioral_cover.status",
        "submodular_interface.status",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Portfolio constraint certification requires this field.",
            )

    selected = set(value_at(certificate, "selection") or [])
    graph: nx.Graph[str] = nx.Graph()
    tokens = value_at(certificate, "tokens")
    if isinstance(tokens, list):
        for token in tokens:
            if isinstance(token, str):
                graph.add_node(token)
    conflicts = value_at(certificate, "conflicts")
    if isinstance(conflicts, list):
        for edge in conflicts:
            if not isinstance(edge, Mapping):
                continue
            left = edge.get("left")
            right = edge.get("right")
            if isinstance(left, str) and isinstance(right, str):
                graph.add_edge(left, right)
    selected_conflicts = [
        (left, right) for left, right in graph.edges if left in selected and right in selected
    ]

    report.require(
        "ConflictFreeSelection",
        not selected_conflicts,
        "selection",
        "Selected portfolio must not contain conflicting token pairs.",
    )
    report.require(
        "BreadthPartitionOK",
        status_is(certificate, "breadth_partition.status", "valid"),
        "breadth_partition.status",
        "Breadth must be evaluated on a declared valid partition.",
    )
    report.require(
        "CherryPickingCleared",
        status_is(certificate, "cherry_picking.status", "cleared"),
        "cherry_picking.status",
        "Portfolio selection must clear cherry-picking audit.",
    )
    report.require(
        "BehavioralCoverOK",
        status_is(certificate, "behavioral_cover.status", "valid"),
        "behavioral_cover.status",
        "Behavioral covering or metric-entropy ledger must be valid.",
    )
    report.require(
        "SubmodularInterfaceOK",
        status_is(certificate, "submodular_interface.status", "valid", "not_required"),
        "submodular_interface.status",
        "Submodular selection interface must be valid or explicitly not required.",
    )
    report.artifacts["selected_conflicts"] = selected_conflicts
    report.metrics["selected_count"] = len(selected)
    report.metrics["conflict_count"] = graph.number_of_edges()
    return report

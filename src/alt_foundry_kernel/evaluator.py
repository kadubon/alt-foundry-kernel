"""Evaluator hierarchy, root rotation, and self-certification-cycle checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import networkx as nx

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, present, status_is


def validate_evaluator_hierarchy(certificate: Mapping[str, Any]) -> CertificateReport:
    """Validate stratified evaluator hierarchy and independent root rotation."""

    report = CertificateReport(
        name="evaluator",
        claim="stratified evaluator hierarchy certificate",
        level="settlement",
    )
    required = (
        "root.status",
        "root_rotation.status",
        "evaluators",
        "evaluation_edges",
    )
    for path in required:
        if not present(certificate, path):
            report.add_issue(
                IssueSeverity.ERROR,
                "required-field-missing",
                path,
                "Evaluator hierarchy certification requires this field.",
            )

    evaluators_raw = certificate.get("evaluators")
    edges_raw = certificate.get("evaluation_edges")
    strata: dict[str, int] = {}
    graph: nx.DiGraph[str] = nx.DiGraph()
    if isinstance(evaluators_raw, list):
        for item in evaluators_raw:
            if not isinstance(item, Mapping):
                continue
            evaluator_id = item.get("id")
            stratum = item.get("stratum")
            if isinstance(evaluator_id, str) and isinstance(stratum, int):
                strata[evaluator_id] = stratum
                graph.add_node(evaluator_id)
    if isinstance(edges_raw, list):
        for item in edges_raw:
            if not isinstance(item, Mapping):
                continue
            evaluator = item.get("evaluator")
            subject = item.get("subject")
            if isinstance(evaluator, str) and isinstance(subject, str):
                graph.add_edge(evaluator, subject)

    acyclic = nx.is_directed_acyclic_graph(graph)
    stratified = all(strata.get(left, -1) > strata.get(right, 10**9) for left, right in graph.edges)
    self_edges = [(left, right) for left, right in graph.edges if left == right]

    report.require(
        "RootOK",
        status_is(certificate, "root.status", "valid"),
        "root.status",
        "Evaluator root must be valid.",
    )
    report.require(
        "RootRotationOK",
        status_is(certificate, "root_rotation.status", "valid"),
        "root_rotation.status",
        "Independent evaluator-root rotation must be valid.",
    )
    report.require(
        "EvaluatorGraphAcyclic",
        acyclic,
        "evaluation_edges",
        "Evaluator hierarchy must be acyclic.",
    )
    report.require(
        "StratifiedEdgesOK",
        stratified,
        "evaluation_edges",
        "Evaluator edges must point from higher independent strata to lower strata.",
    )
    report.require(
        "SelfCertificationCycleFree",
        not self_edges,
        "evaluation_edges",
        "Evaluator graph must not contain self-certification edges.",
    )
    report.metrics["evaluator_count"] = len(strata)
    report.metrics["evaluation_edge_count"] = graph.number_of_edges()
    return report

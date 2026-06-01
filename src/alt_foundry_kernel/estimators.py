"""Deterministic estimator helpers that emit ALT certificate reports.

These helpers turn small declared JSON inputs into certificate-shaped reports.
They are intentionally conservative: they check generic arithmetic and evidence
preconditions, but they do not manufacture causal identification,
transportability, recombination evidence, root authority, or CARA realization.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from math import ceil, sqrt
from typing import Any

import networkx as nx
import numpy as np
from scipy import stats

from alt_foundry_kernel.constants import IssueSeverity
from alt_foundry_kernel.reports import CertificateReport, numeric, value_at
from alt_foundry_kernel.reproduction import capacity_capped_growth
from alt_foundry_kernel.statistics import (
    bounded_mean_report,
    empirical_bernstein_lower_bound,
)


def estimate_certificate(kind: str, payload: Mapping[str, Any]) -> CertificateReport:
    """Dispatch a v0.4.0 estimator kind."""

    checker = ESTIMATORS.get(kind)
    if checker is None:
        report = CertificateReport(name="estimator", claim="unknown estimator", level="evidence")
        report.add_issue(IssueSeverity.ERROR, "unknown-estimator", "kind", kind)
        return report
    return checker(payload)


def estimate_finite_sample(payload: Mapping[str, Any]) -> CertificateReport:
    """Build a bounded empirical lower-bound certificate."""

    values = _float_list(value_at(payload, "values"))
    lower = numeric(payload, "bounds.lower")
    upper = numeric(payload, "bounds.upper")
    confidence = numeric(payload, "confidence") or 0.95
    selected_from = int(numeric(payload, "selected_from") or 1)
    if values is None or lower is None or upper is None:
        return _input_error("finite_sample", "values/bounds", "Finite-sample input is incomplete.")
    report = bounded_mean_report(values, lower, upper, confidence, selected_from)
    report.name = "finite_sample"
    report.claim = "finite-sample operating certificate"
    if report.ok:
        report.artifacts["certificate"] = {
            "schema_hint": "confidence-accounting",
            "values_count": len(values),
            "lower_bound": report.metrics["empirical_bernstein_lower"],
            "adjusted_confidence": report.metrics["adjusted_confidence"],
            "selected_from": selected_from,
        }
    return report


def estimate_proxy_bridge(payload: Mapping[str, Any]) -> CertificateReport:
    """Build a bias-bounded proxy-to-utility bridge report."""

    report = CertificateReport(
        name="proxy_bridge", claim="bias-bounded proxy bridge", level="evidence"
    )
    proxy_lower = numeric(payload, "proxy_effect.lower_bound")
    bias_upper = numeric(payload, "calibration.bias_upper_bound")
    residual_upper = numeric(payload, "calibration.residual_upper_bound") or 0.0
    bridge_status = value_at(payload, "calibration.status")
    lower = (
        proxy_lower - bias_upper - residual_upper
        if proxy_lower is not None and bias_upper is not None
        else None
    )
    report.require(
        "ProxyEffectDeclared",
        proxy_lower is not None,
        "proxy_effect.lower_bound",
        "Proxy effect lower bound is required.",
    )
    report.require(
        "CalibrationBridgeOK",
        bridge_status == "valid",
        "calibration.status",
        "Proxy bridge requires valid calibration.",
    )
    report.require(
        "BridgeLowerBoundPositive",
        lower is not None and lower > 0,
        "calibration.bias_upper_bound",
        "Bias-bounded utility lower bound must be positive.",
    )
    report.metrics.update(
        {
            "proxy_effect_lower_bound": proxy_lower,
            "bias_upper_bound": bias_upper,
            "residual_upper_bound": residual_upper,
            "bridged_lower_bound": lower,
        }
    )
    report.artifacts["certificate"] = {
        "schema_hint": "proxy-bridge-record",
        "status": "valid" if report.ok else "invalid",
        "bridged_lower_bound": lower,
    }
    return report


def estimate_causal_effect(payload: Mapping[str, Any]) -> CertificateReport:
    """Estimate a generic causal-effect certificate under declared mode."""

    mode = value_at(payload, "mode")
    if not isinstance(mode, str):
        return _input_error("causal_estimate", "mode", "Causal estimator mode is required.")
    report = CertificateReport(
        name="causal_estimate", claim=f"{mode} causal effect estimate", level="evidence"
    )
    confidence = numeric(payload, "confidence") or 0.95
    try:
        effects = _causal_effects(mode, payload)
        bound_lower = numeric(payload, "effect_bounds.lower")
        bound_upper = numeric(payload, "effect_bounds.upper")
        if bound_lower is None:
            bound_lower = min(effects)
        if bound_upper is None:
            bound_upper = max(effects)
        if bound_upper <= bound_lower:
            raise ValueError("effect_bounds.upper must be greater than effect_bounds.lower")
        lower = empirical_bernstein_lower_bound(effects, bound_lower, bound_upper, confidence)
    except ValueError as exc:
        report.add_issue(IssueSeverity.ERROR, "causal-input-invalid", "<root>", str(exc))
        return report
    report.require(
        "IdentificationDeclared",
        value_at(payload, "identification.status") == "valid",
        "identification.status",
        "Causal estimates require explicit valid identification status.",
    )
    report.require("SampleOK", len(effects) > 1, "records", "At least two effect records required.")
    report.require(
        "EffectLowerBoundPositive",
        lower > 0,
        "records",
        "Conservative effect lower bound must be positive for settlement-grade evidence.",
    )
    report.metrics.update(
        {"n": len(effects), "effect_mean": float(np.mean(effects)), "effect_lower": lower}
    )
    report.artifacts["certificate"] = {
        "schema_hint": "causal-certificate",
        "mode": mode,
        "effect": {"lower_bound": lower, "unit": value_at(payload, "unit") or "declared-unit"},
        "identification": {"status": value_at(payload, "identification.status")},
    }
    return report


def estimate_transport_diagnostics(payload: Mapping[str, Any]) -> CertificateReport:
    """Estimate support, density-ratio, and finite empirical transport diagnostics."""

    report = CertificateReport(
        name="transport_diagnostics",
        claim="support and Wasserstein-style transport diagnostics",
        level="evidence",
    )
    source = _matrix(value_at(payload, "source_points"))
    target = _matrix(value_at(payload, "target_points"))
    support_radius = numeric(payload, "support.radius")
    radius_threshold = numeric(payload, "wasserstein.radius_threshold")
    if source is None or target is None or support_radius is None or radius_threshold is None:
        report.add_issue(
            IssueSeverity.ERROR,
            "transport-input-invalid",
            "<root>",
            "Transport diagnostics require source_points, target_points, "
            "support radius, and radius threshold.",
        )
        return report
    if source.shape[1] != target.shape[1]:
        report.add_issue(
            IssueSeverity.ERROR,
            "transport-dimension-mismatch",
            "target_points",
            "Source and target points must have the same dimension.",
        )
        return report
    distances = _nearest_distances(source, target)
    empirical_radius = float(np.mean(distances))
    max_gap = float(np.max(distances))
    dimension = int(source.shape[1])
    effective_limit = int(numeric(payload, "dimension.max_effective") or max(1, dimension))
    report.require(
        "SupportCoverageOK",
        max_gap <= support_radius,
        "support.radius",
        "Every target point must be within the declared source support radius.",
    )
    report.require(
        "WassersteinRadiusOK",
        empirical_radius <= radius_threshold,
        "wasserstein.radius_threshold",
        "Empirical transport radius must be below the declared threshold.",
    )
    report.require(
        "EffectiveDimensionOK",
        dimension <= effective_limit,
        "dimension.max_effective",
        "Effective dimension exceeds the declared finite-sample transport limit.",
    )
    report.metrics.update(
        {
            "source_n": int(source.shape[0]),
            "target_n": int(target.shape[0]),
            "dimension": dimension,
            "max_support_gap": max_gap,
            "empirical_transport_radius": empirical_radius,
        }
    )
    report.artifacts["certificate"] = {
        "schema_hint": "transport-diagnostics",
        "support": {"status": "covered" if max_gap <= support_radius else "uncovered"},
        "wasserstein": {
            "radius_upper_bound": empirical_radius,
            "radius_threshold": radius_threshold,
        },
    }
    return report


def estimate_guard_risk(payload: Mapping[str, Any]) -> CertificateReport:
    """Build a split-conformal guard-risk certificate."""

    report = CertificateReport(
        name="guard_risk", claim="split conformal guard risk", level="evidence"
    )
    scores = _float_list(value_at(payload, "calibration_scores"))
    alpha = numeric(payload, "alpha")
    max_risk = numeric(payload, "max_risk")
    if scores is None or alpha is None or max_risk is None or not 0 < alpha < 1:
        report.add_issue(
            IssueSeverity.ERROR,
            "guard-input-invalid",
            "<root>",
            "Guard risk requires calibration_scores, alpha in (0, 1), and max_risk.",
        )
        return report
    index = min(len(scores) - 1, max(0, ceil((len(scores) + 1) * (1.0 - alpha)) - 1))
    threshold = float(np.sort(np.asarray(scores))[index])
    risk_upper = alpha
    report.require(
        "CalibrationSampleOK",
        len(scores) >= 2,
        "calibration_scores",
        "At least two calibration scores are required.",
    )
    report.require(
        "GuardRiskOK",
        risk_upper <= max_risk,
        "max_risk",
        "Declared conformal risk upper bound exceeds the guard budget.",
    )
    report.metrics.update(
        {"n": len(scores), "threshold": threshold, "risk_upper_bound": risk_upper}
    )
    report.artifacts["certificate"] = {
        "schema_hint": "guard-risk-record",
        "threshold": threshold,
        "risk_upper_bound": risk_upper,
    }
    return report


def estimate_federated_pooling(payload: Mapping[str, Any]) -> CertificateReport:
    """Pool independent or correlated evidence using an effective sample penalty."""

    report = CertificateReport(
        name="federated_pooling", claim="federated evidence pooling", level="evidence"
    )
    records = value_at(payload, "records")
    confidence = numeric(payload, "confidence") or 0.95
    rho = numeric(payload, "correlation_upper_bound") or 0.0
    if not isinstance(records, list) or not records:
        return _input_error("federated_pooling", "records", "Pooling requires records.")
    means: list[float] = []
    variances: list[float] = []
    counts: list[float] = []
    for item in records:
        if not isinstance(item, Mapping):
            continue
        mean = _as_float(item.get("mean"))
        variance = _as_float(item.get("variance"))
        count = _as_float(item.get("n"))
        if mean is None or variance is None or count is None or variance <= 0 or count <= 0:
            return _input_error("federated_pooling", "records", "Invalid pooling record.")
        means.append(mean)
        variances.append(variance)
        counts.append(count)
    if not 0 <= rho < 1:
        return _input_error(
            "federated_pooling", "correlation_upper_bound", "Correlation must be in [0, 1)."
        )
    weights = np.asarray([n / v for n, v in zip(counts, variances, strict=True)], dtype=float)
    pooled = float(np.average(np.asarray(means, dtype=float), weights=weights))
    effective_n = float(sum(counts) / (1.0 + max(0, len(counts) - 1) * rho))
    pooled_variance = float(1.0 / np.sum(weights))
    radius = float(stats.norm.ppf((1.0 + confidence) / 2.0) * sqrt(pooled_variance))
    lower = pooled - radius
    report.require(
        "EffectiveSampleOK", effective_n > 1, "records", "Effective sample size must exceed one."
    )
    report.require(
        "PooledLowerBoundPositive",
        lower > 0,
        "records",
        "Pooled lower bound must be positive.",
    )
    report.metrics.update(
        {
            "pooled_mean": pooled,
            "pooled_lower": lower,
            "effective_n": effective_n,
            "correlation_upper_bound": rho,
        }
    )
    report.artifacts["certificate"] = {
        "schema_hint": "federated-pooling",
        "pooled_lower_bound": lower,
        "effective_n": effective_n,
    }
    return report


def estimate_portfolio_selection(payload: Mapping[str, Any]) -> CertificateReport:
    """Greedy conflict-aware portfolio selection with budget accounting."""

    report = CertificateReport(
        name="portfolio_selection", claim="conflict-constrained portfolio selection", level="audit"
    )
    tokens = value_at(payload, "tokens")
    budget = numeric(payload, "budget")
    if not isinstance(tokens, list) or budget is None:
        return _input_error(
            "portfolio_selection", "tokens/budget", "Portfolio input is incomplete."
        )
    conflicts = {
        tuple(sorted((str(item.get("left")), str(item.get("right")))))
        for item in value_at(payload, "conflicts") or []
        if isinstance(item, Mapping)
        and item.get("left") is not None
        and item.get("right") is not None
    }
    selected: list[str] = []
    used_budget = 0.0
    candidates = sorted(
        (_portfolio_item(item) for item in tokens if isinstance(item, Mapping)),
        key=lambda item: item["score"],
        reverse=True,
    )
    for item in candidates:
        token_id = str(item["token_id"])
        if used_budget + float(item["cost"]) > budget:
            continue
        if any(tuple(sorted((token_id, other))) in conflicts for other in selected):
            continue
        selected.append(token_id)
        used_budget += float(item["cost"])
    report.require("BudgetOK", used_budget <= budget, "budget", "Selection must respect budget.")
    report.require("ConflictFreeSelection", True, "conflicts", "Greedy selector skipped conflicts.")
    report.metrics.update({"selected_count": len(selected), "used_budget": used_budget})
    report.artifacts["certificate"] = {
        "schema_hint": "submodular-selection-result",
        "selection": selected,
        "used_budget": used_budget,
    }
    return report


def estimate_foundry_phase(payload: Mapping[str, Any]) -> CertificateReport:
    """Estimate min-cut capacity and phase-control status for a foundry network."""

    report = CertificateReport(
        name="foundry_phase", claim="foundry phase-control estimate", level="audit"
    )
    edges = value_at(payload, "edges")
    source = value_at(payload, "source")
    sink = value_at(payload, "sink")
    demand = numeric(payload, "demand_upper_bound")
    if (
        not isinstance(edges, list)
        or not isinstance(source, str)
        or not isinstance(sink, str)
        or demand is None
    ):
        return _input_error(
            "foundry_phase", "edges", "Foundry phase requires edges, source, sink, and demand."
        )
    graph = nx.DiGraph()
    for item in edges:
        if not isinstance(item, Mapping):
            continue
        left, right, capacity = item.get("from"), item.get("to"), _as_float(item.get("capacity"))
        if (
            isinstance(left, str)
            and isinstance(right, str)
            and capacity is not None
            and capacity >= 0
        ):
            graph.add_edge(left, right, capacity=capacity)
    if source not in graph or sink not in graph:
        return _input_error("foundry_phase", "source/sink", "Source and sink must be in graph.")
    min_cut = float(nx.minimum_cut_value(graph, source, sink, capacity="capacity"))
    slack = min_cut - demand
    phase = "capacity-covered" if slack >= 0 else "capacity-limited"
    report.require(
        "MinCutOK", min_cut >= demand, "demand_upper_bound", "Min-cut must cover demand."
    )
    report.metrics.update(
        {"min_cut_capacity": min_cut, "demand_upper_bound": demand, "slack": slack}
    )
    report.artifacts["certificate"] = {
        "schema_hint": "phase-control-record",
        "phase": phase,
        "min_cut_capacity": min_cut,
        "shadow_price_signal": max(0.0, -slack),
    }
    return report


def estimate_reproduction_phase(payload: Mapping[str, Any]) -> CertificateReport:
    """Estimate reproduction spectral radius and capacity-capped phase."""

    report = CertificateReport(
        name="reproduction_phase",
        claim="reproduction spectral and capacity phase",
        level="evidence",
    )
    matrix = _matrix(value_at(payload, "matrix"))
    state = _float_list(value_at(payload, "state"))
    capacity = _float_list(value_at(payload, "capacity"))
    if matrix is None or state is None or capacity is None:
        return _input_error(
            "reproduction_phase", "matrix/state/capacity", "Reproduction input incomplete."
        )
    try:
        growth = capacity_capped_growth(matrix.tolist(), state, capacity)
        spectral_radius = float(max(abs(np.linalg.eigvals(matrix)))) if matrix.size else 0.0
    except ValueError as exc:
        report.add_issue(IssueSeverity.ERROR, "reproduction-input-invalid", "<root>", str(exc))
        return report
    recombination_claimed = value_at(payload, "recombination.claimed") is True
    recombination_identified = value_at(payload, "recombination.identification_status") == "valid"
    report.require(
        "MatrixNonnegativeOK", bool(np.all(matrix >= 0)), "matrix", "Matrix must be nonnegative."
    )
    report.require(
        "CapacityOK",
        all(item >= 0 for item in capacity),
        "capacity",
        "Capacity must be nonnegative.",
    )
    if recombination_claimed:
        report.require(
            "RecombinationIdentified",
            recombination_identified,
            "recombination.identification_status",
            "Recombination claims require valid identification.",
        )
    else:
        report.predicates["RecombinationIdentified"] = None
    report.metrics.update({"spectral_radius": spectral_radius, "growth_sum": float(sum(growth))})
    report.artifacts["certificate"] = {
        "schema_hint": "recombination-estimate",
        "capacity_capped_growth": growth,
        "spectral_radius": spectral_radius,
        "phase": "supercritical" if spectral_radius > 1 else "subcritical-or-critical",
    }
    return report


def estimate_cara_time_to_target(payload: Mapping[str, Any]) -> CertificateReport:
    """Build a CARA time-to-target certificate from declared trajectories."""

    report = CertificateReport(
        name="cara_time_to_target",
        claim="CARA baseline-envelope and target-time estimate",
        level="settlement",
    )
    candidate = _float_list(value_at(payload, "candidate_path"))
    baseline = _float_list(value_at(payload, "baseline_upper_envelope"))
    target = numeric(payload, "target_threshold")
    margin = numeric(payload, "margin") or 0.0
    raw_net = numeric(payload, "raw_net_capital.lower_bound")
    if candidate is None or baseline is None or target is None or raw_net is None:
        return _input_error("cara_time_to_target", "<root>", "CARA input is incomplete.")
    candidate_time = _first_crossing(candidate, target)
    baseline_time = _first_crossing(baseline, target)
    if baseline_time is None:
        baseline_time = float("inf")
    acceleration = baseline_time - candidate_time if candidate_time is not None else None
    report.require(
        "TargetValidityOK",
        value_at(payload, "target.status") == "valid",
        "target.status",
        "Target status must be valid.",
    )
    report.require(
        "RawNetSolvencyOK",
        raw_net > 0,
        "raw_net_capital.lower_bound",
        "Raw net capital must be positive.",
    )
    report.require(
        "TimeToTargetImprovementOK",
        acceleration is not None and acceleration >= margin,
        "margin",
        "Candidate must cross the target before the baseline envelope by the declared margin.",
    )
    report.metrics.update(
        {
            "candidate_time": candidate_time,
            "baseline_upper_time": None if baseline_time == float("inf") else baseline_time,
            "acceleration_lower_bound": acceleration,
        }
    )
    report.artifacts["certificate"] = {
        "schema_hint": "cara-process",
        "time_to_target": {"acceleration_lower_bound": acceleration},
        "raw_net_capital": {"lower_bound": raw_net},
    }
    return report


def estimate_alpha_budget(payload: Mapping[str, Any]) -> CertificateReport:
    """Check finite alpha/evidence budget spending for settlement."""

    report = CertificateReport(
        name="alpha_budget", claim="finite evidence budget gate", level="audit"
    )
    total = numeric(payload, "alpha_total")
    spent = numeric(payload, "alpha_spent")
    requested = numeric(payload, "alpha_requested")
    if total is None or spent is None or requested is None:
        return _input_error("alpha_budget", "<root>", "Alpha budget fields are required.")
    report.require(
        "AlphaBudgetOK", spent + requested <= total, "alpha_requested", "Alpha budget exhausted."
    )
    report.metrics.update(
        {"alpha_total": total, "alpha_spent": spent, "alpha_requested": requested}
    )
    report.artifacts["certificate"] = {
        "schema_hint": "evidence-budget",
        "alpha_remaining": total - spent - requested,
    }
    return report


def _causal_effects(mode: str, payload: Mapping[str, Any]) -> list[float]:
    records = value_at(payload, "records")
    if not isinstance(records, list) or not records:
        raise ValueError("records are required")
    if mode == "randomized":
        treated = [
            _as_float(item.get("outcome"))
            for item in records
            if isinstance(item, Mapping) and item.get("treatment") is True
        ]
        control = [
            _as_float(item.get("outcome"))
            for item in records
            if isinstance(item, Mapping) and item.get("treatment") is False
        ]
        treated_values = [item for item in treated if item is not None]
        control_values = [item for item in control if item is not None]
        if not treated_values or not control_values:
            raise ValueError("randomized mode requires treatment and control outcomes")
        return [item - float(np.mean(control_values)) for item in treated_values]
    if mode in {"paired", "replay"}:
        diffs = []
        for item in records:
            if not isinstance(item, Mapping):
                continue
            candidate = _as_float(item.get("candidate") or item.get("treated"))
            baseline = _as_float(item.get("baseline") or item.get("control"))
            if candidate is not None and baseline is not None:
                diffs.append(candidate - baseline)
        if not diffs:
            raise ValueError(f"{mode} mode requires paired candidate/baseline records")
        return diffs
    if mode in {"off_policy", "doubly_robust"}:
        effects = []
        for item in records:
            if not isinstance(item, Mapping):
                continue
            reward = _as_float(item.get("reward"))
            target_prob = _as_float(item.get("target_prob"))
            logging_prob = _as_float(item.get("logging_prob"))
            if reward is None or target_prob is None or logging_prob is None or logging_prob <= 0:
                raise ValueError("off-policy records require positive logging_prob")
            weight = target_prob / logging_prob
            if mode == "doubly_robust":
                q_target = _as_float(item.get("outcome_model_target"))
                q_logging = _as_float(item.get("outcome_model_logging"))
                if q_target is None or q_logging is None:
                    raise ValueError("doubly robust records require outcome models")
                effects.append(q_target + weight * (reward - q_logging))
            else:
                effects.append(weight * reward)
        if (
            min(
                _as_float(item.get("logging_prob")) or 0.0
                for item in records
                if isinstance(item, Mapping)
            )
            <= 0
        ):
            raise ValueError("overlap is required")
        return effects
    raise ValueError(f"unsupported causal mode {mode!r}")


def _portfolio_item(item: Mapping[str, Any]) -> dict[str, float | str]:
    token_id = str(item.get("token_id"))
    value = _as_float(item.get("value_lower_bound")) or 0.0
    cost = _as_float(item.get("cost_upper_bound")) or 0.0
    risk = _as_float(item.get("risk_upper_bound")) or 0.0
    net = value - cost - risk
    score = net / max(cost, 1e-12)
    return {"token_id": token_id, "cost": cost, "score": score}


def _nearest_distances(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    return np.asarray(
        [np.min(np.linalg.norm(source - point, axis=1)) for point in target], dtype=float
    )


def _first_crossing(values: Sequence[float], threshold: float) -> float | None:
    for index, value in enumerate(values):
        if value >= threshold:
            return float(index)
    return None


def _float_list(value: Any) -> list[float] | None:
    if not isinstance(value, list) or not value:
        return None
    result: list[float] = []
    for item in value:
        number = _as_float(item)
        if number is None:
            return None
        result.append(number)
    return result


def _matrix(value: Any) -> np.ndarray | None:
    if not isinstance(value, list) or not value:
        return None
    rows: list[list[float]] = []
    for row in value:
        floats = _float_list(row)
        if floats is None:
            return None
        rows.append(floats)
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        return None
    return np.asarray(rows, dtype=float)


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _input_error(name: str, path: str, message: str) -> CertificateReport:
    report = CertificateReport(name=name, claim=f"{name} estimator", level="evidence")
    report.add_issue(IssueSeverity.ERROR, "estimator-input-invalid", path, message)
    return report


ESTIMATORS: dict[str, Callable[[Mapping[str, Any]], CertificateReport]] = {
    "finite-sample": estimate_finite_sample,
    "proxy-bridge": estimate_proxy_bridge,
    "causal-effect": estimate_causal_effect,
    "transport-diagnostics": estimate_transport_diagnostics,
    "guard-risk": estimate_guard_risk,
    "federated-pooling": estimate_federated_pooling,
    "portfolio-selection": estimate_portfolio_selection,
    "foundry-phase": estimate_foundry_phase,
    "reproduction-phase": estimate_reproduction_phase,
    "cara-time-to-target": estimate_cara_time_to_target,
    "alpha-budget": estimate_alpha_budget,
}

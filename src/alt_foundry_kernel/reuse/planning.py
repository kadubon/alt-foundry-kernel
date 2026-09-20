"""Exact finite nonadaptive batch selection over registered correlated scenarios."""

from __future__ import annotations

from fractions import Fraction

from .contracts import Contract, Plan, Score
from .premises import identity, validate
from .qualification import qualify
from .wire import unique


def evaluate(contract: Contract, selected: list[str]) -> Score:
    unique(selected)
    by_id = {item.id: item for item in contract.options}
    if not set(selected) <= by_id.keys():
        raise ValueError("unknown selected option")
    chosen = [by_id[name] for name in sorted(selected)]
    reasons: set[str] = set()
    if contract.unresolved_work:
        reasons.add("unresolved-history")
    cost_ids = set(contract.sunk_cost_ids)
    occupancy: dict[tuple[str, int], int] = {}
    offers = {item.id: item for item in contract.qualifications}
    for option in chosen:
        if set(option.opportunities) & set(contract.completed_opportunities):
            reasons.add("already-completed")
        cost_ids.update(option.costs)
        if not set(option.prerequisites) <= set(selected):
            reasons.add("missing-prerequisite")
        if any(by_id[parent].end > option.start for parent in option.prerequisites):
            reasons.add("prerequisite-timing")
        if set(option.conflicts) & set(selected):
            reasons.add("conflict")
        if not option.hazard_cleared:
            reasons.add("noncompensable-hazard")
        for item in option.occupancy:
            key = (item.resource, item.slot)
            occupancy[key] = occupancy.get(key, 0) + item.quantity
        if option.offer is not None:
            qualification = offers[option.offer]
            try:
                qualify(
                    qualification.request,
                    qualification.candidate,
                    qualification.offer,
                    contract.checkpoint,
                )
            except ValueError:
                reasons.add("missing-receiver-evidence")
            if qualification.offer.valid_until <= contract.checkpoint + option.end:
                reasons.add("expired-qualification")
    for option in chosen:
        if (
            option.offer is not None
            and not set(offers[option.offer].offer.required_cost_ids) <= cost_ids
        ):
            reasons.add("omitted-lifecycle-cost")
    if any(
        quantity > contract.capacities[resource] for (resource, _), quantity in occupancy.items()
    ):
        reasons.add("shared-capacity")
    costs = {unit: Fraction() for unit in contract.budgets}
    incremental = Fraction()
    for cost in contract.costs:
        if cost.id in cost_ids:
            costs[cost.unit] += Fraction(cost.amount)
            if cost.id not in contract.sunk_cost_ids:
                incremental += Fraction(cost.amount) * Fraction(contract.cost_rates[cost.unit])
    if any(amount > Fraction(contract.budgets[unit]) for unit, amount in costs.items()):
        reasons.add("budget")
    lifecycle = sum(
        (amount * Fraction(contract.cost_rates[unit]) for unit, amount in costs.items()), Fraction()
    )
    coverage: dict[str, list[str]] = {}
    nets: dict[str, str] = {}
    opportunities = {item.id: item for item in contract.opportunities}
    for scenario in contract.scenarios:
        active: set[str] = set()
        for option in sorted(chosen, key=lambda item: (item.end, item.id)):
            if option.succeeds[scenario] and set(option.prerequisites) <= active:
                active.add(option.id)
        attained: set[str] = set(contract.completed_opportunities)
        for opportunity in contract.opportunities:
            providers = [
                item
                for item in chosen
                if opportunity.id in item.opportunities
                and item.id in active
                and item.end <= opportunity.deadline
            ]
            if len(providers) > 1:
                reasons.add("overlapping-opportunity")
            if providers:
                attained.add(opportunity.id)
        for bundle in contract.bundles:
            if set(bundle.options) <= active and all(
                by_id[name].end <= opportunities[bundle.opportunity].deadline
                for name in bundle.options
            ):
                if bundle.opportunity in attained:
                    reasons.add("overlapping-opportunity")
                attained.add(bundle.opportunity)
        if any(item.required and item.id not in attained for item in contract.opportunities):
            reasons.add("required-service")
        coverage[scenario] = sorted(attained)
        nets[scenario] = str(
            sum(
                (
                    Fraction(opportunities[name].value[scenario])
                    for name in attained
                    if name not in contract.completed_opportunities
                ),
                Fraction(),
            )
            - incremental
        )
    return Score(
        feasible=not reasons,
        reasons=sorted(reasons),
        costs={unit: str(amount) for unit, amount in costs.items()},
        incremental_cost=str(incremental),
        lifecycle_cost=str(lifecycle),
        scenario_net=nets,
        scenario_coverage=coverage,
    )


def select(contract: Contract, catalogue: str = "all") -> Plan:
    validate(contract)
    if catalogue not in {"all", "scratch", "available", "no-transfer"}:
        raise ValueError("unknown comparator catalogue")
    allowed = {
        "all": {"scratch", "available", "formation", "transfer", "refresh", "reuse"},
        "scratch": {"scratch"},
        "available": {"scratch", "available"},
        "no-transfer": {"scratch", "available", "formation", "refresh", "reuse"},
    }
    options = sorted(item.id for item in contract.options if item.kind in allowed[catalogue])
    best: tuple[Fraction, Fraction] | None = None
    best_score: Score | None = None
    selected: list[str] = []
    expanded = min(2 ** len(options), contract.expansion_limit)
    for mask in range(expanded):
        choice = [name for bit, name in enumerate(options) if mask & (1 << bit)]
        score = evaluate(contract, choice)
        rank = (
            min(Fraction(value) for value in score.scenario_net.values()),
            -Fraction(score.incremental_cost),
        )
        if score.feasible and (best is None or rank > best):
            selected, best_score, best = choice, score, rank
    return Plan(
        version="alt_reuse_plan_v1",
        contract_digest=identity(contract),
        state_digest=contract.initial_revision,
        selected=selected,
        score=best_score,
        expanded=expanded,
        complete=expanded == 2 ** len(options),
        catalogue=catalogue,  # type: ignore[arg-type]
        evidence_basis="declared-model",
        source_authentication=None,
        statistical_coverage=None,
        causal_attribution=None,
        settlement=None,
        execution_authority=None,
    )


def compare(contract: Contract) -> dict[str, Plan]:
    return {name: select(contract, name) for name in ("all", "scratch", "available", "no-transfer")}


def comparison_report(contract: Contract) -> dict[str, object]:
    from .checker import check_plan

    plans = compare(contract)
    candidate = plans["all"]
    margins: dict[str, str | None] = {}
    for name, baseline in plans.items():
        if baseline.score is not None:
            check_plan(contract, baseline)
        if (
            candidate.score is not None
            and baseline.score is not None
            and (candidate.complete and baseline.complete)
        ):
            margins[name] = str(
                min(
                    Fraction(candidate.score.scenario_net[s])
                    - Fraction(baseline.score.scenario_net[s])
                    for s in contract.scenarios
                )
            )
        else:
            margins[name] = None
    return {
        "version": "alt_reuse_comparison_v1",
        "contract_digest": identity(contract),
        "plans": {name: plan.model_dump() for name, plan in plans.items()},
        "joint_scenario_surplus": margins,
        "unit": contract.value_unit,
        "evidence_basis": "declared-model",
        "global_claim_outside_catalogue": None,
        "statistical_coverage": None,
        "causal_attribution": None,
        "execution_authority": None,
    }

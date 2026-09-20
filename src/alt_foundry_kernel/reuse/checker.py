"""Independent option/cost/scenario reconstruction, never imports the selector."""

from __future__ import annotations

from fractions import Fraction

from .contracts import Contract, Plan, Score
from .premises import identity, validate
from .qualification import qualify
from .wire import unique


def check_plan(contract: Contract, plan: Plan) -> dict[str, object]:
    Plan.model_validate(plan.model_dump())
    validate(contract)
    if contract.unresolved_work:
        raise ValueError("unresolved history prevents finite net bound")
    if plan.contract_digest != identity(contract) or plan.state_digest != contract.initial_revision:
        raise ValueError("plan source or state mismatch")
    unique(plan.selected)
    options = {item.id: item for item in contract.options}
    if not set(plan.selected) <= options.keys() or plan.score is None:
        raise ValueError("no checkable incumbent")
    selected = set(plan.selected)
    rows = [options[name] for name in selected]
    allowed = {
        "all": {"scratch", "available", "formation", "transfer", "refresh", "reuse"},
        "scratch": {"scratch"},
        "available": {"scratch", "available"},
        "no-transfer": {"scratch", "available", "formation", "refresh", "reuse"},
    }
    if any(item.kind not in allowed[plan.catalogue] for item in rows):
        raise ValueError("comparator catalogue mismatch")
    paid = set(contract.sunk_cost_ids) | {cost for item in rows for cost in item.costs}
    for item in rows:
        if set(item.opportunities) & set(contract.completed_opportunities):
            raise ValueError("already completed opportunity")
        if (
            not item.hazard_cleared
            or set(item.conflicts) & selected
            or not set(item.prerequisites) <= selected
            or any(options[parent].end > item.start for parent in item.prerequisites)
        ):
            raise ValueError("unsafe dependency or conflict")
        if item.offer is not None:
            registration = next(q for q in contract.qualifications if q.id == item.offer)
            qualify(
                registration.request,
                registration.candidate,
                registration.offer,
                contract.checkpoint,
            )
            if not set(registration.offer.required_cost_ids) <= paid or (
                registration.offer.valid_until <= contract.checkpoint + item.end
            ):
                raise ValueError("omitted cost or expired dependency")
    for resource, bound in contract.capacities.items():
        for slot in range(contract.horizon):
            count = sum(
                occupancy.quantity
                for item in rows
                for occupancy in item.occupancy
                if occupancy.resource == resource and occupancy.slot == slot
            )
            if count > bound:
                raise ValueError("joint resource limit")
    charges = {
        unit: sum(
            (
                Fraction(cost.amount)
                for cost in contract.costs
                if cost.id in paid and cost.unit == unit
            ),
            Fraction(),
        )
        for unit in contract.budgets
    }
    if any(charges[unit] > Fraction(bound) for unit, bound in contract.budgets.items()):
        raise ValueError("consumable budget")
    full = sum(
        (amount * Fraction(contract.cost_rates[unit]) for unit, amount in charges.items()),
        Fraction(),
    )
    sunk = sum(
        (
            Fraction(cost.amount) * Fraction(contract.cost_rates[cost.unit])
            for cost in contract.costs
            if cost.id in contract.sunk_cost_ids
        ),
        Fraction(),
    )
    net: dict[str, str] = {}
    coverage: dict[str, list[str]] = {}
    visits = 0
    for scenario in contract.scenarios:

        def succeeds(name: str, scenario: str = scenario) -> bool:
            nonlocal visits
            visits += 1
            if visits > contract.checker_work_limit:
                raise ValueError("checker dependency work budget exhausted")
            item = options[name]
            return (
                name in selected
                and item.succeeds[scenario]
                and all(succeeds(parent) for parent in item.prerequisites)
            )

        credited: list[str] = []
        for opportunity in contract.opportunities:
            count = int(opportunity.id in contract.completed_opportunities) + sum(
                1
                for item in rows
                if opportunity.id in item.opportunities
                and item.end <= opportunity.deadline
                and succeeds(item.id)
            )
            count += sum(
                1
                for bundle in contract.bundles
                if bundle.opportunity == opportunity.id
                and all(
                    succeeds(name) and options[name].end <= opportunity.deadline
                    for name in bundle.options
                )
            )
            if count > 1 or (opportunity.required and count == 0):
                raise ValueError("overlap or service floor")
            if count == 1:
                credited.append(opportunity.id)
        coverage[scenario] = sorted(credited)
        value = sum(
            (
                Fraction(item.value[scenario])
                for item in contract.opportunities
                if item.id in credited and item.id not in contract.completed_opportunities
            ),
            Fraction(),
        )
        net[scenario] = str(value - full + sunk)
    recomputed = Score(
        feasible=True,
        reasons=[],
        costs={key: str(value) for key, value in charges.items()},
        incremental_cost=str(full - sunk),
        lifecycle_cost=str(full),
        scenario_net=net,
        scenario_coverage=coverage,
    )
    if recomputed != plan.score:
        raise ValueError("saved score differs from reconstructed accounting")
    return {
        "ok": True,
        "contract_digest": identity(contract),
        "score": recomputed.model_dump(),
        "optimality": None,
        "dependency_visits": visits,
        "search_claim_authenticated": False,
        "settlement": None,
        "execution_authority": None,
    }

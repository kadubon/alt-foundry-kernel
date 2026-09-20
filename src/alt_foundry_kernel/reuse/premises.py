"""Registered finite premise checks shared by selector and verifier."""

from __future__ import annotations

from fractions import Fraction

from .contracts import Contract
from .formation import request_identity
from .wire import digest, nonnegative, unique


def identity(contract: Contract) -> str:
    value = contract.model_dump(mode="json")
    for key in ("opportunities", "options", "qualifications", "costs"):
        value[key] = sorted(value[key], key=lambda item: item["id"])
    value["scenarios"] = sorted(value["scenarios"])
    value["sunk_cost_ids"] = sorted(value["sunk_cost_ids"])
    value["completed_opportunities"] = sorted(value["completed_opportunities"])
    value["unresolved_work"] = sorted(value["unresolved_work"])
    for option in value["options"]:
        for key in ("prerequisites", "opportunities", "costs", "conflicts"):
            option[key] = sorted(option[key])
        option["occupancy"] = sorted(
            option["occupancy"], key=lambda item: (item["resource"], item["slot"], item["quantity"])
        )
    for row in value["qualifications"]:
        original = next(q for q in contract.qualifications if q.id == row["id"])
        row["request"] = {"canonical_request_digest": request_identity(original.request)}
        for key in (
            "inputs",
            "opportunities",
            "restrictions",
            "dependencies",
            "preconditions",
            "postconditions",
            "required_cost_ids",
        ):
            row["offer"][key] = sorted(row["offer"][key])
        row["offer"]["checks"] = sorted(row["offer"]["checks"], key=lambda item: item["sha256"])
    for bundle in value["bundles"]:
        bundle["options"] = sorted(bundle["options"])
    value["bundles"] = sorted(value["bundles"], key=lambda item: item["opportunity"])
    return digest(value)


def validate(contract: Contract) -> None:
    Contract.model_validate(contract.model_dump())
    unique(contract.scenarios)
    for items in (
        contract.options,
        contract.opportunities,
        contract.qualifications,
        contract.costs,
    ):
        unique([item.id for item in items])
    if len({item.receiver for item in contract.opportunities}) > 8:
        raise ValueError("receiver bound")
    if contract.evidence_cutoff > contract.checkpoint or Fraction(contract.slot_seconds) <= 0:
        raise ValueError("invalid checkpoint or clock")
    if not 1 <= len(contract.budgets) <= 8 or len(contract.capacities) > 8:
        raise ValueError("resource coordinate bound")
    if set(contract.budgets) != set(contract.cost_rates):
        raise ValueError("incomplete valuation")
    nonnegative([*contract.budgets.values(), *contract.cost_rates.values()])
    costs = {item.id: item for item in contract.costs}
    if not set(contract.sunk_cost_ids) <= costs.keys():
        raise ValueError("unknown sunk cost")
    for cost in contract.costs:
        nonnegative([cost.amount, *cost.allocations.values()])
        if cost.unit not in contract.budgets or sum(
            (Fraction(v) for v in cost.allocations.values()), Fraction()
        ) != Fraction(cost.amount):
            raise ValueError("cost allocation not conserved")
    options = {item.id: item for item in contract.options}
    opportunities = {item.id: item for item in contract.opportunities}
    unique(contract.completed_opportunities)
    if not set(contract.completed_opportunities) <= opportunities.keys():
        raise ValueError("unknown initial completed opportunity")
    offers = {item.id: item for item in contract.qualifications}
    for opportunity in contract.opportunities:
        if set(opportunity.value) != set(contract.scenarios):
            raise ValueError("joint scenario values incomplete")
    for qualification in contract.qualifications:
        if qualification.request.cutoff > contract.evidence_cutoff:
            raise ValueError("formation after frozen evidence cutoff")
        comparator = options.get(qualification.offer.comparator)
        if (
            comparator is None
            or comparator.kind not in {"scratch", "available"}
            or not set(qualification.offer.opportunities) <= set(comparator.opportunities)
        ):
            raise ValueError("missing matched comparator")
        if qualification.offer.mission != contract.scope or (
            qualification.offer.valuation != contract.valuation
        ):
            raise ValueError("qualification contract mismatch")
        if (
            qualification.request.cost_id not in costs
            or costs[qualification.request.cost_id].amount != qualification.request.cost
            or costs[qualification.request.cost_id].unit != qualification.request.cost_unit
        ):
            raise ValueError("formation charge omitted or changed")
    for option in contract.options:
        for values in (option.prerequisites, option.opportunities, option.costs, option.conflicts):
            unique(values)
        if (
            not set(option.prerequisites + option.conflicts) <= options.keys()
            or not set(option.opportunities) <= opportunities.keys()
            or not set(option.costs) <= costs.keys()
        ):
            raise ValueError("unknown option reference")
        if not 0 <= option.start < option.end <= contract.horizon or set(option.succeeds) != set(
            contract.scenarios
        ):
            raise ValueError("unsupported timing or scenario shape")
        if any(
            item.resource not in contract.capacities or not option.start <= item.slot < option.end
            for item in option.occupancy
        ):
            raise ValueError("unknown resource or occupancy outside duration")
        if option.offer is not None and option.offer not in offers:
            raise ValueError("unknown qualification")
        if option.kind in {"reuse", "available"} and option.offer is None:
            raise ValueError("reuse needs receiver evidence")
        if option.offer is not None:
            offer = offers[option.offer].offer
            for op_id in option.opportunities:
                opportunity = opportunities[op_id]
                if (
                    (
                        opportunity.receiver,
                        opportunity.context,
                        opportunity.task_family,
                        opportunity.quality,
                        opportunity.estimand,
                    )
                    != (
                        offer.receiver,
                        offer.context,
                        offer.task_family,
                        offer.quality,
                        offer.estimand,
                    )
                    or opportunity.input_digest not in offer.inputs
                    or op_id not in offer.opportunities
                ):
                    raise ValueError("receiver or service contract mismatch")
        visited: set[str] = set()

        def visit(name: str, path: set[str], visited: set[str] = visited) -> None:
            if name in path:
                raise ValueError("dependency cycle")
            if name in visited:
                return
            visited.add(name)
            for parent in options[name].prerequisites:
                visit(parent, path | {name})

        visit(option.id, set())
    for bundle in contract.bundles:
        unique(bundle.options)
        if bundle.opportunity not in opportunities or not set(bundle.options) <= options.keys():
            raise ValueError("unknown AND bundle")

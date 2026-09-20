"""Finite synthetic break-even controls with actual source-bound receiver records."""

from __future__ import annotations

from typing import Any

from .checker import check_plan
from .contracts import Contract
from .formation import Formation, form
from .lifecycle import empty
from .planning import compare, select
from .wire import digest, envelope


def formation_example() -> Formation:
    traces = []
    for index in (1, 2):
        traces.append(
            envelope(
                {
                    "version": "alt_reuse_trace_v1",
                    "episode": f"episode-{index}",
                    "task": "typed-identity",
                    "input_digest": digest(index),
                    "source_version": "v1",
                    "time": index,
                    "split": "training",
                    "complete": True,
                    "checked_artifact": digest("immutable-identity-implementation"),
                    "steps": [
                        {
                            "primitive": "identity",
                            "arguments": [{"kind": "integer", "value": index}],
                        }
                    ],
                    "outcome": "success",
                    "check_results": ["pass"],
                    "costs": ["formation"],
                    "guards": ["integer-only"],
                    "dependencies": [],
                    "unresolved": [],
                    "secret_taint": False,
                }
            )
        )
    return Formation.model_validate(
        {
            "version": "alt_reuse_formation_v1",
            "mode": "sequence",
            "scope": "synthetic-mission",
            "cutoff": 2,
            "sources": [item.model_dump() for item in traces],
            "library": [
                {
                    "id": "identity",
                    "implementation": digest("immutable-identity-implementation"),
                    "inputs": ["integer"],
                    "output": "integer",
                }
            ],
            "parameters": [{"name": "x", "step": 0, "argument": 0}],
            "attempt_id": "extract-1",
            "cost_id": "formation",
            "cost_unit": "resource",
            "cost": "12",
            "expansion_limit": 16,
        }
    )


def contract_example(uses: int = 4, transfer_cost: int = 0) -> Contract:
    if not 1 <= uses <= 4 or transfer_cost < 0:
        raise ValueError("example supports one to four uses and nonnegative transfer")
    request = formation_example()
    candidate = form(request)
    source_digest = digest(candidate)
    costs: list[dict[str, Any]] = [
        {
            "id": "formation",
            "stage": "formation",
            "unit": "resource",
            "amount": "12",
            "allocations": {"A": "6", "B": "6"},
        }
    ]
    costs.append(
        {
            "id": "transfer",
            "stage": "transfer",
            "unit": "resource",
            "amount": str(transfer_cost),
            "allocations": {"B": str(transfer_cost)},
        }
    )
    options: list[dict[str, Any]] = []
    qualifications = []
    opportunities = []
    for index in range(uses):
        receiver = "A" if index % 2 == 0 else "B"
        name = f"use-{index}"
        check = {
            "version": "alt_reuse_check_v1",
            "candidate": source_digest,
            "receiver": receiver,
            "mission": request.scope,
            "context": "context-v1",
            "task_family": "typed-identity",
            "input_digest": digest(index + 10),
            "protocol": "check-v1",
            "evaluator": "independent-checker-v1",
            "time": 3,
            "result": "pass",
            "restrictions": ["local-only"],
            "dependencies": [],
            "defeaters": [],
            "evidence_basis": "synthetic",
            "quality": "exact",
            "estimand": "one-correct-identity",
            "valuation": "synthetic-resource-v1",
            "preconditions": ["integer-only"],
            "postconditions": ["same-integer"],
        }
        offer = {
            "version": "alt_reuse_offer_v1",
            "candidate": source_digest,
            "receiver": receiver,
            "mission": request.scope,
            "context": "context-v1",
            "task_family": "typed-identity",
            "inputs": [digest(index + 10)],
            "opportunities": [name],
            "protocol": "check-v1",
            "evaluator": "independent-checker-v1",
            "valid_from": 3,
            "valid_until": 100,
            "restrictions": ["local-only"],
            "dependencies": [],
            "preconditions": ["integer-only"],
            "postconditions": ["same-integer"],
            "checks": [envelope(check).model_dump()],
            "required_cost_ids": ["formation", f"reuse-cost-{index}"]
            + (["transfer"] if receiver == "B" else []),
            "comparator": f"scratch-{index}",
            "estimand": "one-correct-identity",
            "quality": "exact",
            "valuation": "synthetic-resource-v1",
            "evidence_basis": "synthetic",
        }
        qualifications.append(
            {
                "id": name,
                "request": request.model_dump(),
                "candidate": candidate.model_dump(),
                "offer": offer,
            }
        )
        opportunities.append(
            {
                "id": name,
                "receiver": receiver,
                "context": "context-v1",
                "input_digest": digest(index + 10),
                "task_family": "typed-identity",
                "task": "identity-task",
                "quality": "exact",
                "estimand": "one-correct-identity",
                "deadline": 8,
                "required": True,
                "value": {"deterministic": "10"},
            }
        )
        for kind, amount in (("scratch", "5"), ("reuse", "1")):
            cost_id = f"{kind}-cost-{index}"
            costs.append(
                {
                    "id": cost_id,
                    "stage": "execution",
                    "unit": "resource",
                    "amount": amount,
                    "allocations": {receiver: amount},
                }
            )
            options.append(
                {
                    "id": f"{kind}-{index}",
                    "kind": kind,
                    "prerequisites": []
                    if kind == "scratch"
                    else ["prepare"] + (["adapt-B"] if receiver == "B" else []),
                    "offer": name if kind == "reuse" else None,
                    "opportunities": [name],
                    "costs": [cost_id],
                    "occupancy": [{"resource": "verifier", "slot": index + 2, "quantity": 1}],
                    "start": index + 2,
                    "end": index + 3,
                    "succeeds": {"deterministic": True},
                    "hazard_cleared": True,
                    "conflicts": [],
                }
            )
    for name, kind, start, cost_id, parents in (
        ("prepare", "formation", 0, "formation", []),
        ("adapt-B", "transfer", 1, "transfer", ["prepare"]),
    ):
        options.append(
            {
                "id": name,
                "kind": kind,
                "prerequisites": parents,
                "offer": None,
                "opportunities": [],
                "costs": [cost_id],
                "occupancy": [],
                "start": start,
                "end": start + 1,
                "succeeds": {"deterministic": True},
                "hazard_cleared": True,
                "conflicts": [],
            }
        )
    return Contract.model_validate(
        {
            "version": "alt_reuse_contract_v1",
            "scope": request.scope,
            "study": "synthetic-study",
            "split": "training",
            "checkpoint": 3,
            "evidence_cutoff": 3,
            "initial_revision": digest(empty(request.scope, "synthetic-study")),
            "time_origin": "synthetic-clock",
            "slot_seconds": "1",
            "horizon": 8,
            "valuation": "synthetic-resource-v1",
            "value_unit": "resource",
            "cost_rates": {"resource": "1"},
            "budgets": {"resource": "100"},
            "capacities": {"verifier": 1},
            "scenarios": ["deterministic"],
            "opportunities": opportunities,
            "options": options,
            "bundles": [],
            "qualifications": qualifications,
            "costs": costs,
            "sunk_cost_ids": [],
            "objective": "worst-net-value-then-cost",
            "joint_model": "registered-separable-opportunities",
            "expansion_limit": 4096,
            "execution_authority": None,
        }
    )


def example() -> dict[str, Any]:
    contract = contract_example()
    plans = compare(contract)
    checks = {name: check_plan(contract, plan) for name, plan in plans.items()}
    costly = contract_example(transfer_cost=5)
    costly_plan = select(costly)
    check_plan(costly, costly_plan)
    return {
        "contract": contract.model_dump(),
        "plans": {name: plan.model_dump() for name, plan in plans.items()},
        "checks": checks,
        "costly_transfer_plan": costly_plan.model_dump(),
        "writes": False,
        "empirical_acceleration": None,
        "execution_authority": None,
    }


def history_example() -> Any:
    from .lifecycle import Event, replay

    contract = contract_example()
    journal = empty(contract.scope, contract.study)
    row = contract.qualifications[0]
    defaults: dict[str, Any] = {
        "version": "alt_reuse_event_v1",
        "scope": contract.scope,
        "study": contract.study,
        "time": 3,
        "recorded": 3,
        "artifact": row.candidate.artifact_digest,
        "receiver": "A",
        "context": "context-v1",
        "task": "identity-task",
        "input_digest": row.offer.inputs[0],
        "protocol": row.offer.protocol,
        "evaluator": row.offer.evaluator,
        "offer_digest": digest(row.offer),
        "attempt": "prepare",
        "outcome": "success",
        "dependencies": [],
        "required_cost_ids": [],
        "cost_id": None,
        "cost_unit": None,
        "quantity": "1",
        "valid_until": 100,
        "target": None,
        "origin": {"endogenous": "0", "external": "0", "unresolved": "1"},
        "evidence_basis": "synthetic",
    }

    def append(**fields: Any) -> None:
        event = Event.model_validate({**defaults, **fields, "previous": digest(journal)})
        journal.events.append(envelope(event))

    for cost in contract.costs:
        if not cost.id.startswith("scratch"):
            append(
                id="charge-" + cost.id,
                kind="cost",
                cost_id=cost.id,
                cost_unit=cost.unit,
                quantity=cost.amount,
                cost_stage=cost.stage,
            )
    for qualification in contract.qualifications:
        offer = qualification.offer
        append(
            id="qualify-" + qualification.id,
            kind="qualify",
            receiver=offer.receiver,
            input_digest=offer.inputs[0],
            offer_digest=digest(offer),
            qualification=qualification.model_dump(),
            required_cost_ids=offer.required_cost_ids,
        )
    append(id="created", kind="formation", required_cost_ids=["formation"])
    for index, qualification in enumerate(contract.qualifications):
        offer = qualification.offer
        args = {
            "receiver": offer.receiver,
            "input_digest": offer.inputs[0],
            "offer_digest": digest(offer),
            "attempt": "attempt-" + qualification.id,
            "required_cost_ids": offer.required_cost_ids,
        }
        append(
            id="request-" + qualification.id,
            kind="request",
            time=4 + index * 2,
            recorded=4 + index * 2,
            **args,
        )
        append(
            id="result-" + qualification.id,
            kind="result",
            time=5 + index * 2,
            recorded=5 + index * 2,
            **args,
        )
    replay(journal, 20)
    return journal

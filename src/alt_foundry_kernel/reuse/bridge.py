"""Journal-aware replanning and read-only connection to the established ALT kernel."""

from __future__ import annotations

from typing import Any

from alt_foundry_kernel.constants import LifecycleState
from alt_foundry_kernel.models import KernelState

from .contracts import Contract, Plan
from .lifecycle import Journal, replay
from .planning import select
from .wire import digest


def inspect_kernel(state: KernelState) -> dict[str, Any]:
    current = sorted(
        {
            name
            for name in state.admitted_tokens
            if state.token_states.get(name) == LifecycleState.ACTIVE
        }
    )
    return {
        "legacy_cumulative_capital": state.certified_capital,
        "legacy_current_tokens": current,
        "receiver_qualified_stock": None,
        "new_profile_eligibility": None,
        "settlement_write": False,
        "reason": "Legacy declarations do not supply source-bound receiver qualification.",
    }


def at_history(contract: Contract, journal: Journal) -> Contract:
    state = replay(journal, contract.evidence_cutoff)
    if (
        contract.initial_revision != digest(journal)
        or contract.scope != journal.scope
        or (contract.study != journal.study)
    ):
        raise ValueError("history checkpoint mismatch; new mission cannot reset obligations")
    costs = {cost.id: cost for cost in contract.costs}
    for cost_id, charge in state["costs"].items():
        if (
            cost_id not in costs
            or costs[cost_id].amount != charge["amount"]
            or (costs[cost_id].unit != charge["unit"] or cost_id not in contract.sunk_cost_ids)
        ):
            raise ValueError("historical charge omitted or changed")
    result = contract.model_copy(deep=True)
    result.unresolved_work = state["unresolved"]
    result.completed_opportunities = sorted(
        {
            op.id
            for op in contract.opportunities
            if any(
                (row[1], row[2], row[3], row[4])
                == (op.receiver, op.context, op.task, op.input_digest)
                for row in state["successful_uses"]
            )
        }
    )
    eligible = {row["offer_digest"] for row in state["eligible"].values()}
    offers = {q.id: q for q in contract.qualifications}
    for item in result.options:
        if item.offer is not None:
            offer = offers[item.offer]
            if journal.events and digest(offer.offer) not in eligible:
                item.succeeds = {scenario: False for scenario in contract.scenarios}
            if offer.candidate.artifact_digest in state["revoked"]:
                item.succeeds = {scenario: False for scenario in contract.scenarios}
    if state["unresolved"]:
        # No invented reservation release: unresolved local work blocks this bounded batch.
        for item in result.options:
            item.hazard_cleared = False
    return result


def replan(contract: Contract, journal: Journal) -> Plan:
    return select(at_history(contract, journal))

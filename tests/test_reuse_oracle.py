from __future__ import annotations

from fractions import Fraction
from itertools import product

from hypothesis import given, settings
from hypothesis import strategies as st

from alt_foundry_kernel.reuse.checker import check_plan
from alt_foundry_kernel.reuse.examples import contract_example
from alt_foundry_kernel.reuse.planning import select


@settings(max_examples=30, deadline=None)
@given(st.lists(st.integers(0, 15), min_size=2, max_size=2), st.integers(0, 20))
def test_separately_written_tiny_oracle(prices: list[int], setup: int) -> None:
    contract = contract_example(2)
    contract.costs[0].amount = str(setup)
    contract.costs[0].allocations = {"A": str(setup)}
    for row in contract.qualifications:
        row.request.cost = str(setup)
        from alt_foundry_kernel.reuse.formation import form
        from alt_foundry_kernel.reuse.wire import digest, envelope

        row.candidate = form(row.request)
        row.offer.candidate = digest(row.candidate)
        evidence = row.offer.checks[0].read()
        evidence["candidate"] = row.offer.candidate
        row.offer.checks[0] = envelope(evidence)
    for index, price in enumerate(prices):
        cost = next(c for c in contract.costs if c.id == f"reuse-cost-{index}")
        cost.amount = str(price)
        cost.allocations = {"A" if index == 0 else "B": str(price)}
    # This oracle enumerates per-opportunity technological choices, not production subsets.
    totals = []
    for decisions in product((False, True), repeat=2):
        total = setup if any(decisions) else 0
        total += sum(prices[i] if reuse else 5 for i, reuse in enumerate(decisions))
        totals.append(total)
    plan = select(contract)
    assert plan.score is not None
    assert Fraction(plan.score.lifecycle_cost) == min(totals)
    assert check_plan(contract, plan)["ok"]

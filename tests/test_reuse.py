from __future__ import annotations

from copy import deepcopy
from fractions import Fraction

import pytest

from alt_foundry_kernel.reuse.checker import check_plan
from alt_foundry_kernel.reuse.examples import contract_example, formation_example
from alt_foundry_kernel.reuse.formation import form, reconstruct
from alt_foundry_kernel.reuse.planning import compare, select
from alt_foundry_kernel.reuse.qualification import qualify
from alt_foundry_kernel.reuse.wire import digest, envelope, loads, rational


@pytest.mark.parametrize(("uses", "expected"), [(1, "5"), (2, "10"), (3, "15"), (4, "16")])
def test_matched_break_even(uses: int, expected: str) -> None:
    contract = contract_example(uses)
    plan = select(contract)
    assert plan.score is not None
    assert plan.score.lifecycle_cost == expected
    assert check_plan(contract, plan)["ok"] is True
    baseline = select(contract, "scratch")
    assert baseline.score is not None
    assert Fraction(baseline.score.lifecycle_cost) == 5 * uses


def test_transfer_cost_changes_choice() -> None:
    contract = contract_example(transfer_cost=5)
    plan = select(contract)
    assert plan.selected == [f"scratch-{i}" for i in range(4)]
    assert check_plan(contract, plan)["ok"]


def test_parameterized_reconstruction_and_permutation() -> None:
    request = formation_example()
    candidate = form(request)
    assert reconstruct(request, candidate)
    request.sources.reverse()
    assert form(request) == candidate
    bad = candidate.model_copy(deep=True)
    bad.representation[0].arguments[0].value = "wrong"
    with pytest.raises(ValueError, match="projection"):
        reconstruct(request, bad)


@pytest.mark.parametrize("change", ["holdout", "incomplete", "failed", "taint", "digest"])
def test_source_bound_controls(change: str) -> None:
    request = formation_example()
    raw = request.sources[0].read()
    if change == "holdout":
        raw["split"] = "holdout"
    elif change == "incomplete":
        raw["complete"] = False
    elif change == "failed":
        raw["check_results"] = ["fail"]
    elif change == "taint":
        raw["secret_taint"] = True
    request.sources[0] = envelope(raw)
    if change == "digest":
        request.sources[0].sha256 = "0" * 64
    if change in {"holdout", "digest"}:
        with pytest.raises(ValueError):
            form(request)
    else:
        assert form(request).qualification == "unqualified"


def test_receiver_cannot_inherit_a() -> None:
    contract = contract_example()
    row = contract.qualifications[0]
    row.offer.receiver = "C"
    with pytest.raises(ValueError, match="mismatch"):
        qualify(row.request, row.candidate, row.offer, 3)


def test_joint_capacity_and_incomplete_search() -> None:
    contract = contract_example()
    contract.capacities["verifier"] = 0
    assert select(contract).score is None
    contract = contract_example()
    contract.expansion_limit = 1
    plan = select(contract)
    assert not plan.complete
    assert plan.score is None  # no-op does not satisfy required work
    for opportunity in contract.opportunities:
        opportunity.required = False
    plan = select(contract)
    assert not plan.complete and plan.selected == []
    assert check_plan(contract, plan)["optimality"] is None


def test_score_forgery_and_cost_omission() -> None:
    contract = contract_example()
    plan = select(contract)
    assert plan.score is not None
    plan.score.lifecycle_cost = "4"
    with pytest.raises(ValueError, match="accounting"):
        check_plan(contract, plan)
    plan = select(contract)
    plan.selected.remove("prepare")
    with pytest.raises(ValueError):
        check_plan(contract, plan)


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', "NaN", "1.5", '{"x":Infinity}'])
def test_strict_json(text: str) -> None:
    with pytest.raises(ValueError):
        loads(text)


@pytest.mark.parametrize("value", ["1/2", "0", "-3", "42"])
def test_rational(value: str) -> None:
    assert rational(value) == value


@pytest.mark.parametrize("value", ["2/4", "-0", "01", "1.2", "1/0", "9" * 82])
def test_bad_rational(value: str) -> None:
    with pytest.raises(ValueError):
        rational(value)


def test_catalogue_order_invariance() -> None:
    contract = contract_example(2)
    first = compare(contract)
    other = deepcopy(contract)
    other.options.reverse()
    other.costs.reverse()
    assert compare(other) == first
    assert digest(contract) != digest(other)  # raw ordering differs; declared set identity does not

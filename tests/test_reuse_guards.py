from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from alt_foundry_kernel.reuse.checker import check_plan
from alt_foundry_kernel.reuse.contracts import Bundle
from alt_foundry_kernel.reuse.examples import contract_example, formation_example
from alt_foundry_kernel.reuse.formation import Atom, Parameter, form, reconstruct
from alt_foundry_kernel.reuse.planning import evaluate, select
from alt_foundry_kernel.reuse.premises import identity, validate
from alt_foundry_kernel.reuse.qualification import Adapter, adapt, qualify
from alt_foundry_kernel.reuse.wire import digest, envelope, loads


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("slot_seconds", "0"),
        ("evidence_cutoff", 10),
        ("budgets", {}),
        ("cost_rates", {}),
        ("sunk_cost_ids", ["absent"]),
        ("scenarios", ["deterministic", "deterministic"]),
    ],
)
def test_registration_guard(field: str, value: Any) -> None:
    contract = contract_example(1)
    setattr(contract, field, value)
    with pytest.raises(ValueError):
        validate(contract)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("prerequisites", ["absent"]),
        ("prerequisites", ["scratch-0"]),
        ("offer", "unknown"),
        ("start", 10),
        ("succeeds", {}),
        ("opportunities", ["unknown"]),
        ("costs", ["unknown"]),
    ],
)
def test_option_registration_guard(field: str, value: Any) -> None:
    contract = contract_example(1)
    setattr(contract.options[0], field, value)
    with pytest.raises(ValueError):
        validate(contract)


@pytest.mark.parametrize(
    "case",
    [
        "allocation",
        "unit",
        "negative",
        "scenario",
        "scope",
        "formation",
        "resource",
        "no-offer",
        "receiver",
        "bundle",
    ],
)
def test_closed_premises(case: str) -> None:
    contract = contract_example(1)
    if case == "allocation":
        contract.costs[0].allocations = {"A": "1"}
    elif case == "unit":
        contract.costs[0].unit = "undeclared"
    elif case == "negative":
        contract.costs[0].amount = "-12"
    elif case == "scenario":
        contract.opportunities[0].value = {}
    elif case == "scope":
        contract.qualifications[0].offer.mission = "other"
    elif case == "formation":
        contract.qualifications[0].request.cost = "1"
    elif case == "resource":
        contract.options[0].occupancy[0].resource = "missing"
    elif case == "no-offer":
        contract.options[1].offer = None
    elif case == "receiver":
        contract.opportunities[0].receiver = "C"
    else:
        contract.bundles = [Bundle(opportunity="missing", options=["scratch-0"])]
    with pytest.raises(ValueError):
        validate(contract)


def test_overlap_and_and_bundle_are_joint() -> None:
    contract = contract_example(1)
    score = evaluate(contract, ["scratch-0", "reuse-0", "prepare"])
    assert not score.feasible and "overlapping-opportunity" in score.reasons
    contract.options[0].opportunities = []
    contract.qualifications = []
    contract.options = [item for item in contract.options if item.kind != "reuse"]
    contract.bundles = [Bundle(opportunity="use-0", options=["scratch-0", "prepare"])]
    plan = select(contract)
    assert plan.score is not None and check_plan(contract, plan)["ok"]
    contract.bundles.append(contract.bundles[0])
    assert not evaluate(contract, ["scratch-0", "prepare"]).feasible


@pytest.mark.parametrize("case", ["conflict", "hazard", "timing", "budget", "expiry", "evidence"])
def test_independent_checker_rejects_infeasible_changes(case: str) -> None:
    contract = contract_example(4)
    plan = select(contract)
    if case == "conflict":
        contract.options[-1].conflicts = ["prepare"]
    elif case == "hazard":
        contract.options[-1].hazard_cleared = False
    elif case == "timing":
        contract.options[-1].end = 5
    elif case == "budget":
        contract.budgets["resource"] = "1"
    elif case == "expiry":
        contract.qualifications[0].offer.valid_until = 4
    else:
        check = contract.qualifications[0].offer.checks[0].read()
        check["result"] = "fail"
        contract.qualifications[0].offer.checks[0] = envelope(check)
    plan.contract_digest = identity(contract)
    assert not evaluate(contract, plan.selected).feasible
    with pytest.raises(ValueError):
        check_plan(contract, plan)


def test_checker_does_not_authenticate_search_or_settlement() -> None:
    contract = contract_example()
    plan = select(contract)
    plan.contract_digest = "0" * 64
    with pytest.raises(ValueError, match="mismatch"):
        check_plan(contract, plan)
    plan = select(contract)
    plan.catalogue = "scratch"
    with pytest.raises(ValueError, match="catalogue"):
        check_plan(contract, plan)
    plan = select(contract)
    plan.execution_authority = True  # type: ignore[assignment]
    with pytest.raises(ValueError):
        check_plan(contract, plan)
    with pytest.raises(ValueError):
        select(contract, "imaginary")
    with pytest.raises(ValueError):
        evaluate(contract, ["imaginary"])


@pytest.mark.parametrize(
    "case",
    ["arity", "primitive", "reference", "type", "forward", "holdout", "cost", "deps", "duplicate"],
)
def test_trace_shape_and_evidence(case: str) -> None:
    request = formation_example()
    raw = request.sources[0].read()
    if case == "arity":
        raw["steps"][0]["arguments"] = []
    elif case == "primitive":
        raw["steps"][0]["primitive"] = "shell"
    elif case in {"reference", "forward"}:
        raw["steps"][0]["arguments"][0] = {"kind": "reference", "value": 0}
    elif case == "type":
        raw["steps"][0]["arguments"][0]["value"] = "not-an-integer"
    elif case == "holdout":
        raw["time"] = 100
    elif case == "cost":
        request.cost = "-1"
    elif case == "deps":
        raw["dependencies"] = [digest("unavailable")]
    elif case == "duplicate":
        request.sources[1] = request.sources[0]
    request.sources[0] = envelope(raw)
    with pytest.raises(ValueError):
        form(request)


def test_extraction_bounds_packaging_and_failed_attempt() -> None:
    request = formation_example()
    request.expansion_limit = 1
    with pytest.raises(ValueError, match="budget"):
        form(request)
    request = formation_example()
    request.parameters = []
    with pytest.raises(ValueError, match="recurring"):
        form(request)
    request = formation_example()
    request.parameters.append(request.parameters[0])
    with pytest.raises(ValueError, match="duplicate"):
        form(request)
    request = formation_example()
    request.parameters[0].step = 7
    with pytest.raises(ValueError, match="outside"):
        form(request)
    request = formation_example()
    request.sources.pop()
    with pytest.raises(ValueError, match="recurrence"):
        form(request)
    request.mode = "package"
    with pytest.raises(ValueError, match="packaging"):
        form(request)
    request.parameters = []
    assert reconstruct(request, form(request))


def test_repeated_variable_and_dataflow() -> None:
    request = formation_example()
    request.library[0].inputs = ["integer", "integer"]
    request.parameters.append(Parameter(name="x", step=0, argument=1))
    for index, source in enumerate(request.sources):
        raw = source.read()
        raw["steps"][0]["arguments"].append({"kind": "integer", "value": index + 1})
        request.sources[index] = envelope(raw)
    assert reconstruct(request, form(request))
    raw = request.sources[0].read()
    raw["steps"][0]["arguments"][1]["value"] = 9
    request.sources[0] = envelope(raw)
    with pytest.raises(ValueError, match="equality"):
        form(request)


@pytest.mark.parametrize(
    "field",
    [
        "request_digest",
        "source_digests",
        "implementation_digests",
        "guards",
        "source_cost_ids",
        "formation_cost_id",
        "qualification",
    ],
)
def test_reconstruction_tampering(field: str) -> None:
    request = formation_example()
    candidate = form(request)
    values: dict[str, Any] = {
        "request_digest": "0" * 64,
        "source_digests": [],
        "implementation_digests": [],
        "guards": [],
        "source_cost_ids": [],
        "formation_cost_id": "missing",
        "qualification": "unqualified",
    }
    setattr(candidate, field, values[field])
    with pytest.raises(ValueError):
        reconstruct(request, candidate)


def test_reconstruction_truncation_and_literal_change() -> None:
    request = formation_example()
    candidate = form(request)
    candidate.representation = []
    with pytest.raises(ValueError, match="truncation"):
        reconstruct(request, candidate)
    request.sources.pop()
    request.mode = "package"
    request.parameters = []
    candidate = form(request)
    candidate.representation[0].arguments[0] = Atom(kind="integer", value=10)
    with pytest.raises(ValueError, match="projection"):
        reconstruct(request, candidate)


@pytest.mark.parametrize(
    "case",
    [
        "candidate",
        "mission",
        "expired",
        "guards",
        "formation",
        "failure",
        "defeater",
        "input",
        "duplicate",
    ],
)
def test_qualification_narrowing(case: str) -> None:
    row = contract_example(1).qualifications[0]
    if case == "candidate":
        row.offer.candidate = "0" * 64
    elif case == "mission":
        row.offer.mission = "other"
    elif case == "expired":
        row.offer.valid_until = 3
    elif case == "guards":
        row.offer.preconditions = []
    elif case == "formation":
        row.offer.required_cost_ids = ["use"]
    elif case in {"failure", "defeater"}:
        raw = row.offer.checks[0].read()
        raw["result" if case == "failure" else "defeaters"] = (
            "unknown" if case == "failure" else ["bad"]
        )
        row.offer.checks[0] = envelope(raw)
    elif case == "input":
        row.offer.inputs = [digest("other")]
    else:
        row.offer.inputs *= 2
    with pytest.raises(ValueError):
        qualify(row.request, row.candidate, row.offer, 3)


def test_explicit_unit_mapping_and_losses() -> None:
    adapter = Adapter.model_validate(
        {
            "version": "alt_reuse_adapter_v1",
            "fields": [
                {
                    "source": "seconds",
                    "target": "minutes",
                    "source_unit": "s",
                    "target_unit": "min",
                    "scale": "1/60",
                }
            ],
            "allowed_units": ["s", "min"],
        }
    )
    result = adapt(adapter, {"seconds": "90", "unused": "2"})
    assert result["values"] == {"minutes": "3/2"}
    assert result["unmapped_fields"] == ["unused"]
    with pytest.raises(ValueError):
        adapt(adapter, {})
    bad = deepcopy(adapter)
    bad.fields[0].scale = "0"
    with pytest.raises(ValueError):
        adapt(bad, {"seconds": "90"})


@pytest.mark.parametrize(
    "raw",
    [
        '"' + "a" * 2000000 + '"',
        "[" * 26 + "0" + "]" * 26,
        "[" * 1100 + "0" + "]" * 1100,
        str(2**129),
    ],
    ids=["bytes", "depth", "recursion", "integer"],
)
def test_parser_work_bounds(raw: str) -> None:
    with pytest.raises(ValueError):
        loads(raw)

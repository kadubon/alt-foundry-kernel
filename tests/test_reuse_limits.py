import pytest

from alt_foundry_kernel.reuse.checker import check_plan
from alt_foundry_kernel.reuse.examples import contract_example, formation_example
from alt_foundry_kernel.reuse.formation import form, reconstruct
from alt_foundry_kernel.reuse.planning import select
from alt_foundry_kernel.reuse.premises import identity


def test_renaming_and_source_repackaging_do_not_create_stock() -> None:
    request = formation_example()
    first = form(request)
    request.attempt_id = "renamed-attempt"
    request.parameters[0].name = "renamed-parameter"
    second = form(request)
    assert first.artifact_digest == second.artifact_digest
    assert first.request_digest != second.request_digest
    assert reconstruct(request, second)
    second.artifact_digest = "0" * 64
    with pytest.raises(ValueError, match="identity"):
        reconstruct(request, second)


def test_independent_checker_work_budget() -> None:
    contract = contract_example()
    plan = select(contract)
    contract.checker_work_limit = 1
    plan.contract_digest = identity(contract)
    with pytest.raises(ValueError, match="work budget"):
        check_plan(contract, plan)


def test_reconstruction_work_and_position_bounds() -> None:
    request = formation_example()
    candidate = form(request)
    request.expansion_limit = 1
    with pytest.raises(ValueError, match="work"):
        reconstruct(request, candidate)
    request.expansion_limit = 16
    request.parameters[0].step = 7
    with pytest.raises(ValueError, match="positions"):
        reconstruct(request, candidate)

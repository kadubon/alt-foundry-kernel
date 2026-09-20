from alt_foundry_kernel.reuse.examples import contract_example
from alt_foundry_kernel.reuse.planning import comparison_report


def test_surplus_requires_complete_matched_comparators() -> None:
    contract = contract_example()
    report = comparison_report(contract)
    assert report["joint_scenario_surplus"]["scratch"] == "4"
    contract.expansion_limit = 1
    report = comparison_report(contract)
    assert report["joint_scenario_surplus"]["scratch"] is None


def test_negative_optional_investments_choose_no_op() -> None:
    from alt_foundry_kernel.reuse.planning import select

    contract = contract_example()
    for opportunity in contract.opportunities:
        opportunity.required = False
        opportunity.value = {"deterministic": "0"}
    assert select(contract).selected == []

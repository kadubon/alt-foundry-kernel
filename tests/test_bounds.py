from alt_foundry_kernel import compute_signed_bounds


def test_signed_lower_bound_uses_upper_charges() -> None:
    report = compute_signed_bounds(
        {
            "value_lower_bound": 12.0,
            "value_upper_bound": 18.0,
            "cost_upper_bound": 3.0,
            "cost_lower_bound": 1.5,
            "risk_upper_bound": 1.0,
            "risk_lower_bound": 0.0,
            "transport_upper_bound": 1.0,
            "transport_lower_bound": 0.0,
        }
    )

    assert report.lower_bound == 7.0
    assert report.upper_bound == 16.5
    assert report.lower_decidable


def test_signed_lower_bound_missing_cost_is_undefined() -> None:
    report = compute_signed_bounds(
        {
            "value_lower_bound": 12.0,
            "risk_upper_bound": 1.0,
            "transport_upper_bound": 1.0,
        }
    )

    assert report.lower_bound is None
    assert "cost_upper_bound" in report.missing_for_lower

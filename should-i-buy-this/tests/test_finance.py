import math

import pytest

from finance import (
    calculate_purchase_impact,
    future_value_annuity,
    future_value_lump_sum,
    get_periods_per_year,
    growth_curve,
    milestone_values,
    num_occurrences,
    total_nominal_cost,
)


def test_get_periods_per_year_known_values():
    assert get_periods_per_year("daily") == 365
    assert get_periods_per_year("weekly") == 52
    assert get_periods_per_year("monthly") == 12


def test_get_periods_per_year_invalid():
    with pytest.raises(ValueError):
        get_periods_per_year("yearly")


def test_future_value_lump_sum_basic():
    # $100 at 10% for 2 years -> 100 * 1.1^2 = 121
    assert future_value_lump_sum(100, 0.10, 2) == pytest.approx(121.0)


def test_future_value_lump_sum_zero_rate():
    assert future_value_lump_sum(50, 0.0, 10) == pytest.approx(50.0)


def test_future_value_lump_sum_zero_years():
    assert future_value_lump_sum(50, 0.07, 0) == pytest.approx(50.0)


def test_future_value_annuity_zero_rate_is_simple_sum():
    # No growth: 12 payments of $10 over 1 year = $120
    assert future_value_annuity(10, 0.0, 1, 12) == pytest.approx(120.0)


def test_future_value_annuity_matches_manual_formula():
    payment, rate, years, periods = 100, 0.06, 5, 12
    n = periods * years
    r = rate / periods
    expected = payment * (((1 + r) ** n - 1) / r)
    assert future_value_annuity(payment, rate, years, periods) == pytest.approx(expected)


def test_future_value_annuity_grows_with_rate():
    low = future_value_annuity(50, 0.02, 10, 12)
    high = future_value_annuity(50, 0.10, 10, 12)
    assert high > low


def test_num_occurrences():
    assert num_occurrences(1, 365) == 365
    assert num_occurrences(2, 52) == 104
    assert num_occurrences(0.5, 12) == 6


def test_total_nominal_cost_one_time():
    assert total_nominal_cost(25, is_recurring=False, years=30) == 25


def test_total_nominal_cost_recurring():
    assert total_nominal_cost(5, is_recurring=True, years=2, periods_per_year=52) == pytest.approx(5 * 104)


def test_calculate_purchase_impact_one_time():
    impact = calculate_purchase_impact(price=1000, is_recurring=False, annual_rate=0.07, years=10)
    assert impact.today_cost == 1000
    assert impact.future_value == pytest.approx(future_value_lump_sum(1000, 0.07, 10))
    assert impact.is_recurring is False
    assert impact.occurrences is None


def test_calculate_purchase_impact_recurring_requires_frequency():
    with pytest.raises(ValueError):
        calculate_purchase_impact(price=5, is_recurring=True, annual_rate=0.07, years=10)


def test_calculate_purchase_impact_recurring():
    impact = calculate_purchase_impact(
        price=5, is_recurring=True, annual_rate=0.07, years=10, frequency="weekly"
    )
    assert impact.occurrences == num_occurrences(10, 52)
    assert impact.today_cost == pytest.approx(5 * impact.occurrences)
    assert impact.future_value_per_occurrence == pytest.approx(impact.future_value / impact.occurrences)


def test_growth_curve_length_and_endpoints():
    curve = growth_curve(price=100, is_recurring=False, annual_rate=0.07, years=5)
    assert len(curve) == 6  # years 0..5 inclusive
    assert curve[0] == (0, pytest.approx(100.0))
    assert curve[-1][0] == 5
    assert curve[-1][1] == pytest.approx(future_value_lump_sum(100, 0.07, 5))


def test_growth_curve_is_monotonically_increasing_for_positive_rate():
    curve = growth_curve(price=10, is_recurring=True, annual_rate=0.07, years=5, frequency="monthly")
    values = [v for _, v in curve]
    assert all(math.isclose(b, a) or b > a for a, b in zip(values, values[1:]))


def test_milestone_values_includes_default_checkpoints_and_horizon():
    milestones = milestone_values(price=100, is_recurring=False, annual_rate=0.07, years=30)
    years_seen = [year for year, _ in milestones]
    assert years_seen == [1, 5, 10, 20, 30]


def test_milestone_values_excludes_checkpoints_past_horizon():
    milestones = milestone_values(price=100, is_recurring=False, annual_rate=0.07, years=3)
    years_seen = [year for year, _ in milestones]
    assert years_seen == [1, 3]


def test_milestone_values_no_duplicate_when_horizon_matches_a_checkpoint():
    milestones = milestone_values(price=100, is_recurring=False, annual_rate=0.07, years=10)
    years_seen = [year for year, _ in milestones]
    assert years_seen == [1, 5, 10]
    assert len(years_seen) == len(set(years_seen))


def test_milestone_values_matches_underlying_formulas():
    milestones = milestone_values(
        price=5, is_recurring=True, annual_rate=0.07, years=10, frequency="weekly"
    )
    for year, value in milestones:
        assert value == pytest.approx(future_value_annuity(5, 0.07, year, 52))

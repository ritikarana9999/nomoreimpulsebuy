import pytest

from finance import (
    FREQUENCY_OPTIONS,
    FREQUENCY_PERIODS_PER_YEAR,
    get_periods_per_year,
    monthly_savings_equivalent,
    savings_breakdown,
    weekly_savings_equivalent,
    yearly_savings_equivalent,
)


def test_get_periods_per_year_known_values():
    assert get_periods_per_year("daily") == 365
    assert get_periods_per_year("weekly") == 52
    assert get_periods_per_year("monthly") == 12
    assert get_periods_per_year("quarterly") == 4
    assert get_periods_per_year("half-yearly") == 2
    assert get_periods_per_year("yearly") == 1


def test_frequency_options_matches_periods_dict():
    assert set(FREQUENCY_OPTIONS) == set(FREQUENCY_PERIODS_PER_YEAR)


def test_get_periods_per_year_invalid():
    with pytest.raises(ValueError):
        get_periods_per_year("fortnightly")


def test_weekly_savings_equivalent_across_frequencies():
    assert weekly_savings_equivalent(1, "daily") == pytest.approx(365 / 52)
    assert weekly_savings_equivalent(7, "weekly") == pytest.approx(7)
    assert weekly_savings_equivalent(50, "monthly") == pytest.approx(50 * 12 / 52)
    assert weekly_savings_equivalent(120, "yearly") == pytest.approx(120 / 52)


def test_monthly_savings_equivalent_across_frequencies():
    assert monthly_savings_equivalent(1, "daily") == pytest.approx(365 / 12)
    assert monthly_savings_equivalent(7, "weekly") == pytest.approx(7 * 52 / 12)
    assert monthly_savings_equivalent(50, "monthly") == pytest.approx(50)
    assert monthly_savings_equivalent(30, "quarterly") == pytest.approx(10)
    assert monthly_savings_equivalent(60, "half-yearly") == pytest.approx(10)
    assert monthly_savings_equivalent(120, "yearly") == pytest.approx(10)


def test_yearly_savings_equivalent_across_frequencies():
    assert yearly_savings_equivalent(1, "daily") == pytest.approx(365)
    assert yearly_savings_equivalent(5, "weekly") == pytest.approx(260)
    assert yearly_savings_equivalent(50, "monthly") == pytest.approx(600)
    assert yearly_savings_equivalent(30, "quarterly") == pytest.approx(120)
    assert yearly_savings_equivalent(60, "half-yearly") == pytest.approx(120)
    assert yearly_savings_equivalent(120, "yearly") == pytest.approx(120)


def test_savings_breakdown_matches_individual_functions():
    breakdown = savings_breakdown(5.50, "weekly")
    assert breakdown["weekly"] == pytest.approx(weekly_savings_equivalent(5.50, "weekly"))
    assert breakdown["monthly"] == pytest.approx(monthly_savings_equivalent(5.50, "weekly"))
    assert breakdown["yearly"] == pytest.approx(yearly_savings_equivalent(5.50, "weekly"))
    assert breakdown["occurrences_per_year"] == 52


def test_savings_breakdown_yearly_is_twelve_times_monthly():
    breakdown = savings_breakdown(20, "monthly")
    assert breakdown["yearly"] == pytest.approx(breakdown["monthly"] * 12)

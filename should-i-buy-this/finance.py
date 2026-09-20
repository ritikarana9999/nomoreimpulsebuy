"""Financial math for "Should I Buy This?".

Pure functions only — no Streamlit, no I/O — so everything here is
independently testable and reusable if the UI ever changes.
"""

from __future__ import annotations

from dataclasses import dataclass

FREQUENCY_PERIODS_PER_YEAR = {
    "daily": 365,
    "weekly": 52,
    "monthly": 12,
}


def get_periods_per_year(frequency: str) -> int:
    """Return how many times a recurring purchase happens per year.

    Args:
        frequency: One of "daily", "weekly", "monthly".

    Returns:
        The number of occurrences per year for that frequency.

    Raises:
        ValueError: If frequency isn't a recognized option.
    """
    try:
        return FREQUENCY_PERIODS_PER_YEAR[frequency]
    except KeyError as exc:
        valid = ", ".join(FREQUENCY_PERIODS_PER_YEAR)
        raise ValueError(f"Unknown frequency {frequency!r}; expected one of: {valid}") from exc


def future_value_lump_sum(price: float, annual_rate: float, years: float) -> float:
    """Future value of a single, one-time purchase amount invested today.

    Uses standard annual compound interest: FV = PV * (1 + r)^t

    Args:
        price: The amount spent today.
        annual_rate: Annual return rate as a decimal (e.g. 0.07 for 7%).
        years: Number of years the money would have been invested.

    Returns:
        The projected future value of that amount.
    """
    return price * (1 + annual_rate) ** years


def future_value_annuity(payment: float, annual_rate: float, years: float, periods_per_year: int) -> float:
    """Future value of a recurring investment made at a fixed frequency.

    Uses the future value of an ordinary annuity, with the annual rate
    converted to a periodic rate based on ``periods_per_year``:

        FV = payment * (((1 + r)^n - 1) / r)

    where r = annual_rate / periods_per_year and n = periods_per_year * years.
    Falls back to a simple sum (no growth) when annual_rate is 0.

    Args:
        payment: The amount spent on each occurrence.
        annual_rate: Annual return rate as a decimal (e.g. 0.07 for 7%).
        years: Number of years contributions continue.
        periods_per_year: How many payments happen per year.

    Returns:
        The projected future value of all the recurring payments.
    """
    n = periods_per_year * years
    if annual_rate == 0:
        return payment * n
    r = annual_rate / periods_per_year
    return payment * (((1 + r) ** n - 1) / r)


def num_occurrences(years: float, periods_per_year: int) -> int:
    """Total number of times a recurring purchase happens over the horizon."""
    return int(round(years * periods_per_year))


def total_nominal_cost(price: float, is_recurring: bool, years: float, periods_per_year: int | None = None) -> float:
    """The plain, un-invested cost of the purchase(s) over the time horizon.

    For a one-time purchase this is just the price. For a recurring
    purchase it's price * how many times it happens, with no growth
    applied — useful as the "today's cost" comparison point.
    """
    if not is_recurring:
        return price
    return price * num_occurrences(years, periods_per_year)


@dataclass
class PurchaseImpact:
    """Result of running a purchase through the opportunity-cost model."""

    today_cost: float
    future_value: float
    years: float
    is_recurring: bool
    occurrences: int | None = None
    future_value_per_occurrence: float | None = None


def calculate_purchase_impact(
    price: float,
    is_recurring: bool,
    annual_rate: float,
    years: float,
    frequency: str | None = None,
) -> PurchaseImpact:
    """Run a purchase through the compound-growth or annuity model.

    Args:
        price: Cost of a single purchase/occurrence.
        is_recurring: Whether this purchase repeats over time.
        annual_rate: Assumed annual investment return, as a decimal.
        years: Time horizon in years.
        frequency: Required when is_recurring is True; one of
            "daily", "weekly", "monthly".

    Returns:
        A PurchaseImpact with today's cost, the projected future value,
        and (for recurring purchases) how many times it happens and the
        future value attributable to each single occurrence.
    """
    if is_recurring:
        if frequency is None:
            raise ValueError("frequency is required when is_recurring is True")
        periods_per_year = get_periods_per_year(frequency)
        future_value = future_value_annuity(price, annual_rate, years, periods_per_year)
        occurrences = num_occurrences(years, periods_per_year)
        today_cost = total_nominal_cost(price, True, years, periods_per_year)
        return PurchaseImpact(
            today_cost=today_cost,
            future_value=future_value,
            years=years,
            is_recurring=True,
            occurrences=occurrences,
            future_value_per_occurrence=future_value / occurrences if occurrences else 0.0,
        )

    future_value = future_value_lump_sum(price, annual_rate, years)
    return PurchaseImpact(
        today_cost=price,
        future_value=future_value,
        years=years,
        is_recurring=False,
    )


def growth_curve(
    price: float,
    is_recurring: bool,
    annual_rate: float,
    years: float,
    frequency: str | None = None,
) -> list[tuple[int, float]]:
    """Year-by-year future value, for plotting the growth curve.

    Returns a list of (year_offset, future_value) pairs from year 0
    through the full time horizon (inclusive), so a chart can show the
    trajectory rather than just the final number.
    """
    total_years = int(years)
    periods_per_year = get_periods_per_year(frequency) if is_recurring else None

    points: list[tuple[int, float]] = []
    for year in range(total_years + 1):
        if is_recurring:
            value = future_value_annuity(price, annual_rate, year, periods_per_year)
        else:
            value = future_value_lump_sum(price, annual_rate, year)
        points.append((year, value))
    return points


def milestone_values(
    price: float,
    is_recurring: bool,
    annual_rate: float,
    years: float,
    frequency: str | None = None,
    checkpoints: tuple[int, ...] = (1, 5, 10, 20),
) -> list[tuple[int, float]]:
    """Future value at a few meaningful checkpoints on the way to the full horizon.

    Returns (year, value) pairs for each checkpoint strictly inside the
    horizon, always ending with the full horizon itself — so callers get
    a short "here's how it grows along the way" list rather than just
    the final number.
    """
    years_int = int(years)
    milestones = sorted({c for c in checkpoints if 0 < c < years_int} | {years_int})

    results: list[tuple[int, float]] = []
    for year in milestones:
        if is_recurring:
            periods_per_year = get_periods_per_year(frequency)
            value = future_value_annuity(price, annual_rate, year, periods_per_year)
        else:
            value = future_value_lump_sum(price, annual_rate, year)
        results.append((year, value))
    return results


# --- Extension points -------------------------------------------------
#
# These are intentionally not implemented yet. They're noted here so the
# shape of the code doesn't need to change much when they're built out.
#
# - happiness_score (1-10): could be threaded through PurchaseImpact and
#   calculate_purchase_impact() to adjust the tone/framing of the output
#   (e.g. a high score softens the copy) without touching the math above.
#
# - log_calculation(impact: PurchaseImpact, ...) -> None: would append each
#   calculation to a local file or SQLite DB for later analysis. Kept out
#   of this module's pure-function design on purpose — it belongs behind
#   a thin storage layer that the UI calls explicitly, not something the
#   math functions do as a side effect.
#
# - custom portfolio rate: annual_rate is already just a plain float
#   parameter everywhere above, so a "use my own rate" toggle in the UI
#   can pass a different number in with no changes needed here.

"""Financial math for "Should I Buy This?".

Pure functions only — no Streamlit, no I/O — so everything here is
independently testable and reusable if the UI ever changes.

No investment growth is assumed anywhere in this module: every figure
is plain cash math (skip the purchase, keep the cash), on purpose —
straightforward beats a compound-interest lecture.
"""

from __future__ import annotations

FREQUENCY_PERIODS_PER_YEAR = {
    "daily": 365,
    "weekly": 52,
    "monthly": 12,
    "quarterly": 4,
    "half-yearly": 2,
    "yearly": 1,
}

FREQUENCY_OPTIONS = tuple(FREQUENCY_PERIODS_PER_YEAR)


def get_periods_per_year(frequency: str) -> int:
    """Return how many times a recurring purchase happens per year.

    Args:
        frequency: One of "daily", "weekly", "monthly", "quarterly",
            "half-yearly", "yearly".

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


def weekly_savings_equivalent(price: float, frequency: str) -> float:
    """Convert a recurring price at any frequency to a plain weekly rate."""
    return price * get_periods_per_year(frequency) / 52


def monthly_savings_equivalent(price: float, frequency: str) -> float:
    """Convert a recurring price at any frequency to a plain monthly rate."""
    return price * get_periods_per_year(frequency) / 12


def yearly_savings_equivalent(price: float, frequency: str) -> float:
    """Convert a recurring price at any frequency to a plain yearly rate."""
    return price * get_periods_per_year(frequency)


def savings_breakdown(price: float, frequency: str) -> dict[str, float]:
    """Plain savings totals if a recurring purchase is skipped.

    Returns a dict with "weekly", "monthly", and "yearly" totals, plus
    "occurrences_per_year" — all simple multiplication, no investment
    growth assumed.
    """
    return {
        "weekly": weekly_savings_equivalent(price, frequency),
        "monthly": monthly_savings_equivalent(price, frequency),
        "yearly": yearly_savings_equivalent(price, frequency),
        "occurrences_per_year": get_periods_per_year(frequency),
    }


# --- Extension points -------------------------------------------------
#
# These are intentionally not implemented yet. They're noted here so the
# shape of the code doesn't need to change much when they're built out.
#
# - happiness_score (1-10): could adjust the tone/framing of the output
#   copy in app.py (e.g. a high score softens the message) without
#   touching the math above.
#
# - log_calculation(breakdown: dict, ...) -> None: would append each
#   calculation to a local file or SQLite DB for later analysis. Kept out
#   of this module's pure-function design on purpose — it belongs behind
#   a thin storage layer that the UI calls explicitly, not something the
#   math functions do as a side effect.

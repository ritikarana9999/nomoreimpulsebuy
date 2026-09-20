"""Streamlit UI for "Should I Buy This?" — an impulse-purchase calculator.

All the math lives in finance.py; this file is just inputs, layout, and copy.
"""

from datetime import date

import pandas as pd
import streamlit as st

from finance import calculate_purchase_impact, growth_curve

st.set_page_config(page_title="Should I Buy This?", page_icon="💸", layout="centered")

st.title("💸 Should I Buy This?")
st.caption("A friendly little calculator, not a guilt trip.")

with st.form("purchase_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        purchase_name = st.text_input("What are you eyeing?", value="Latte", placeholder="e.g. Latte")
    with col2:
        price = st.number_input("Price ($)", min_value=0.01, value=5.50, step=0.5, format="%.2f")

    frequency_choice = st.radio("How often do you buy this?", ["One-time", "Recurring"], horizontal=True)

    frequency = None
    if frequency_choice == "Recurring":
        frequency = st.selectbox("How often?", ["daily", "weekly", "monthly"], index=1)

    annual_rate_pct = st.slider(
        "Assumed annual investment return",
        min_value=2,
        max_value=12,
        value=7,
        step=1,
        format="%d%%",
    )

    years = st.slider("Time horizon (years)", min_value=1, max_value=50, value=30, step=1)

    submitted = st.form_submit_button("Crunch the numbers", use_container_width=True)

if submitted or "last_result" in st.session_state:
    is_recurring = frequency_choice == "Recurring"
    annual_rate = annual_rate_pct / 100

    impact = calculate_purchase_impact(
        price=price,
        is_recurring=is_recurring,
        annual_rate=annual_rate,
        years=years,
        frequency=frequency,
    )

    target_year = date.today().year + years
    name = purchase_name.strip() or "this"

    st.divider()

    if is_recurring:
        st.subheader(f"Your {frequency} {name} habit will cost you \\${impact.future_value:,.0f} by {target_year} 😳")
        st.write(
            f"That's **{impact.occurrences:,} purchases** of \\${price:,.2f} each — "
            f"\\${impact.today_cost:,.2f} out of pocket today, but "
            f"**\\${impact.future_value:,.2f}** if it had grown at {annual_rate_pct}% a year instead."
        )
    else:
        st.subheader(f"That {name} will cost you \\${impact.future_value:,.0f} by {target_year} 😳")
        st.write(
            f"\\${price:,.2f} today could grow into **\\${impact.future_value:,.2f}** "
            f"in {years} years at {annual_rate_pct}% annual return."
        )

    curve = growth_curve(
        price=price,
        is_recurring=is_recurring,
        annual_rate=annual_rate,
        years=years,
        frequency=frequency,
    )
    chart_df = pd.DataFrame(curve, columns=["Year", "Future value ($)"]).set_index("Year")
    st.line_chart(chart_df)

    st.divider()

    if is_recurring:
        st.info(
            f"☕ Fun fact: each \\${price:,.2f} {name.lower()} is secretly a "
            f"**\\${impact.future_value_per_occurrence:,.2f}** {name.lower()}, once you count what it "
            f"could have grown into. No judgment — just math."
        )
    else:
        multiplier = impact.future_value / price if price else 0
        st.info(
            f"🔮 Fun fact: that \\${price:,.2f} is really a **{multiplier:,.1f}x** bet against your future self. "
            f"Could still be worth it — that's your call, not ours."
        )

    st.caption(
        "This is a simple projection, not financial advice — real returns go up and down, "
        "and life is for living too. Buy the latte if the latte is good."
    )

    st.session_state["last_result"] = True

# --- Extension points ---------------------------------------------------
#
# - Happiness score (1-10): a slider could go here to soften/adjust the
#   copy above (e.g. "you clearly love this — enjoy it") without changing
#   the underlying math in finance.py.
#
# - Calculation history: each `impact` computed above could be handed to
#   a small storage helper (local file or SQLite) to log runs for later
#   analysis, without finance.py needing to know about storage at all.
#
# - Custom portfolio rate: `annual_rate` above is a plain float, so a
#   toggle to swap the slider for a user-entered personal return rate
#   just needs to set that same variable before calculate_purchase_impact
#   is called.

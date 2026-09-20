"""Streamlit UI for "Should I Buy This?" — an impulse-purchase calculator.

All the math lives in finance.py; this file is just inputs, layout, and copy.
"""

from datetime import date

import pandas as pd
import streamlit as st

from finance import calculate_purchase_impact, growth_curve

st.set_page_config(page_title="Should I Buy This?", page_icon="🎀", layout="centered")

# Whimsical, girly reskin: pastel gradients, rounded playful fonts, sticker
# emoji, and soft "card" styling — no external images, so nothing here
# depends on a network fetch or borrows anyone else's artwork.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Quicksand:wght@400;500;600;700&display=swap');

    html, body, [class^="css"], [class*=" css"] {
        font-family: 'Quicksand', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 18%, rgba(255, 182, 217, 0.45), transparent 42%),
            radial-gradient(circle at 88% 12%, rgba(199, 178, 255, 0.40), transparent 42%),
            radial-gradient(circle at 50% 95%, rgba(255, 214, 165, 0.30), transparent 45%),
            linear-gradient(180deg, #fffaf7 0%, #fdf3fb 100%);
        background-attachment: fixed;
    }

    h1, h2, h3, .headline-stat, .sticker-row {
        font-family: 'Baloo 2', cursive;
    }

    .sticker-row {
        text-align: center;
        font-size: 1.6rem;
        letter-spacing: 0.4rem;
        margin-bottom: -0.5rem;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.75);
        border-radius: 28px;
        padding: 2rem 1.75rem;
        border: 2px dashed #ffb6d9;
        box-shadow: 0 10px 30px rgba(216, 154, 214, 0.25);
    }

    .stTextInput input, .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 14px !important;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #ff9ecb, #c7b2ff);
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.6rem 1.5rem;
        font-family: 'Baloo 2', cursive;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: 0 6px 16px rgba(255, 158, 203, 0.45);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 10px 22px rgba(199, 178, 255, 0.55);
        color: white;
    }

    .headline-stat {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.3;
        background: linear-gradient(90deg, #ff6fa8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0 1rem 0;
    }

    .stAlert {
        border-radius: 20px !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="sticker-row">✨ 🎀 💕 🌸 💅 ✨</div>', unsafe_allow_html=True)
st.title("Should I Buy This? 🎀")
st.caption("A cute little calculator for your treat-yourself moments 💕 — zero guilt, all sparkle.")

with st.form("purchase_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        purchase_name = st.text_input("🛍️ What are you eyeing?", value="Latte", placeholder="e.g. Latte")
    with col2:
        price = st.number_input("💸 Price ($)", min_value=0.01, value=5.50, step=0.5, format="%.2f")

    frequency_choice = st.radio("🔁 How often do you buy this?", ["One-time ✨", "Recurring 🔁"], horizontal=True)
    is_recurring_choice = frequency_choice.startswith("Recurring")

    frequency = None
    if is_recurring_choice:
        frequency = st.selectbox("📅 How often?", ["daily", "weekly", "monthly"], index=1)

    annual_rate_pct = st.slider(
        "📈 Assumed annual investment return, if you invested instead",
        min_value=2,
        max_value=12,
        value=7,
        step=1,
        format="%d%%",
    )

    years = st.slider("⏳ Time horizon (years)", min_value=1, max_value=50, value=30, step=1)

    submitted = st.form_submit_button("✨ Crunch the Numbers ✨", use_container_width=True)

if submitted or "last_result" in st.session_state:
    is_recurring = frequency_choice.startswith("Recurring")
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
        st.markdown(
            f'<div class="headline-stat">Your {frequency} {name} habit will cost you '
            f"\\${impact.future_value:,.0f} by {target_year} 😳💸</div>",
            unsafe_allow_html=True,
        )
        st.write(
            f"That's **{impact.occurrences:,} purchases** of \\${price:,.2f} each — "
            f"\\${impact.today_cost:,.2f} out of pocket today, but "
            f"**\\${impact.future_value:,.2f}** if it had grown at {annual_rate_pct}% a year instead. 🌸"
        )
    else:
        st.markdown(
            f'<div class="headline-stat">That {name} will cost you '
            f"\\${impact.future_value:,.0f} by {target_year} 😳💸</div>",
            unsafe_allow_html=True,
        )
        st.write(
            f"\\${price:,.2f} today could grow into **\\${impact.future_value:,.2f}** "
            f"in {years} years at {annual_rate_pct}% annual return. 🌸"
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
            f"☕💕 Fun fact: each \\${price:,.2f} {name.lower()} is secretly a "
            f"**\\${impact.future_value_per_occurrence:,.2f}** {name.lower()}, once you count what it "
            f"could have grown into. No judgment — just math. ✨"
        )
    else:
        multiplier = impact.future_value / price if price else 0
        st.info(
            f"🔮💅 Fun fact: that \\${price:,.2f} is really a **{multiplier:,.1f}x** bet against your future self. "
            f"Could still be worth it — that's your call, not ours. ✨"
        )

    st.caption(
        "This is a simple projection, not financial advice — real returns go up and down, "
        "and life is for living too. Buy the latte if the latte is good. 🌸💕"
    )

    st.session_state["last_result"] = True

    if submitted:
        st.balloons()

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

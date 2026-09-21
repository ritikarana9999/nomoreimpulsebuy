"""Streamlit UI for "Should I Buy This?" — an impulse-purchase calculator.

All the math lives in finance.py; this file is just inputs, layout, and copy.
"""

import pandas as pd
import streamlit as st

from finance import FREQUENCY_OPTIONS, monthly_savings_equivalent, savings_breakdown

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
        margin: 0.5rem 0 1rem 0;
    }

    /* Gradient-text trick only applies to the wording, never to emoji —
       color emoji glyphs don't respect text-fill-color and render as
       broken/substituted symbols if caught inside a clipped span. */
    .gradient-text {
        background: linear-gradient(90deg, #ff6fa8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .stAlert {
        border-radius: 20px !important;
        border: none !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        padding: 0.75rem 0.5rem;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        justify-content: center;
    }
    [data-testid="stMetricValue"] {
        color: #ff6fa8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="sticker-row">✨ 🎀 💕 🌸 💅 ✨</div>', unsafe_allow_html=True)
st.title("Should I Buy This? 🎀")
st.caption("A cute little calculator for your treat-yourself moments 💕 — skip it, keep the cash.")

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
        frequency = st.selectbox("📅 How often?", FREQUENCY_OPTIONS, index=1)

    submitted = st.form_submit_button("✨ Crunch the Numbers ✨", use_container_width=True)

if submitted or "last_result" in st.session_state:
    is_recurring = frequency_choice.startswith("Recurring")
    name = purchase_name.strip() or "this"

    st.divider()

    if is_recurring:
        breakdown = savings_breakdown(price=price, frequency=frequency)

        st.markdown(
            f'<div class="headline-stat"><span class="gradient-text">'
            f"Skip your {frequency} {name} and save"
            f"</span> 💰✨</div>",
            unsafe_allow_html=True,
        )

        week_col, month_col, year_col = st.columns(3)
        with week_col:
            st.metric("📅 Per week", f"${breakdown['weekly']:,.2f}")
        with month_col:
            st.metric("🗓️ Per month", f"${breakdown['monthly']:,.2f}")
        with year_col:
            st.metric("🎉 Per year", f"${breakdown['yearly']:,.2f}")

        st.caption(
            f"That's **{breakdown['occurrences_per_year']:,} {name.lower()}s a year** at "
            f"\\${price:,.2f} each — no investing, no market risk, just cash back in your pocket. 🌸"
        )
    else:
        st.markdown(
            f'<div class="headline-stat"><span class="gradient-text">'
            f"Skip that {name} and keep ${price:,.2f}"
            f"</span> 💰✨</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "One-time purchases don't have a weekly/monthly rhythm — but hey, that's "
            f"\\${price:,.2f} staying right in your pocket. 🌸"
        )

    st.caption(
        "Simple and straightforward: this is just what skipping it puts back in your "
        "pocket — no assumptions, no guilt trip. 💕"
    )

    st.session_state["last_result"] = True

    if submitted:
        st.balloons()

st.divider()
st.markdown('<div class="sticker-row">📝 💌 🛍️ ✨</div>', unsafe_allow_html=True)
st.subheader("My Savings List 💌")
st.caption("Add every little splurge you're skipping this month and watch the total add up. ✨")

if "savings_list" not in st.session_state:
    st.session_state.savings_list = pd.DataFrame(
        {
            "Product": pd.Series(dtype="str"),
            "Price ($)": pd.Series(dtype="float"),
            "Frequency": pd.Series(dtype="str"),
        }
    )

edited_savings_list = st.data_editor(
    st.session_state.savings_list,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="savings_list_editor",
    column_config={
        "Product": st.column_config.TextColumn("🛍️ Product", required=True),
        "Price ($)": st.column_config.NumberColumn(
            "💸 Price ($)", min_value=0.01, step=0.5, format="%.2f", required=True
        ),
        "Frequency": st.column_config.SelectboxColumn(
            "🔁 Frequency", options=list(FREQUENCY_OPTIONS), required=True
        ),
    },
)
st.session_state.savings_list = edited_savings_list

complete_rows = edited_savings_list.dropna(subset=["Product", "Price ($)", "Frequency"])
complete_rows = complete_rows[complete_rows["Product"].astype(str).str.strip() != ""]

if not complete_rows.empty:
    complete_rows = complete_rows.copy()
    complete_rows["Monthly savings"] = complete_rows.apply(
        lambda row: monthly_savings_equivalent(row["Price ($)"], row["Frequency"]), axis=1
    )
    total_monthly = complete_rows["Monthly savings"].sum()

    st.markdown(
        f'<div class="headline-stat"><span class="gradient-text">'
        f"Skip it all and save ${total_monthly:,.2f}</span> every month 💰✨</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"That's **\\${total_monthly * 12:,.2f} a year**, just by skipping what's on this list. 🎉")
    st.dataframe(
        complete_rows[["Product", "Price ($)", "Frequency", "Monthly savings"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Price ($)": st.column_config.NumberColumn("💸 Price ($)", format="$%.2f"),
            "Monthly savings": st.column_config.NumberColumn("💰 Monthly savings", format="$%.2f"),
        },
    )
else:
    st.caption("Add a product above (double-click a cell to start) to see your monthly total. 🌸")

# --- Extension points ---------------------------------------------------
#
# - Happiness score (1-10): a slider could go here to soften/adjust the
#   copy above (e.g. "you clearly love this — enjoy it") without changing
#   the underlying math in finance.py.
#
# - Calculation history: each `breakdown` computed above could be handed
#   to a small storage helper (local file or SQLite) to log runs for
#   later analysis, without finance.py needing to know about storage.

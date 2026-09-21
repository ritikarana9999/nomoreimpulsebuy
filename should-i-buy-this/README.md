# Should I Buy This? 💸

A small, playful calculator that shows what skipping a purchase actually
saves you — broken down by week, month, and year.

Not a guilt trip. Not an investing lecture. Just plain, straightforward math.

## What it does

- Pick a purchase (name + price), mark it one-time or recurring
  (daily/weekly/monthly/quarterly/half-yearly/yearly).
- For recurring purchases, shows what skipping it saves **per week, per
  month, and per year** — simple multiplication, no investment growth or
  return-rate assumptions anywhere.
- For one-time purchases, shows the plain amount you'd keep.
- **My Savings List:** an editable table where you can add every product
  you're skipping, at any frequency, and see the combined monthly (and
  yearly) total.

## Project structure

```
should-i-buy-this/
├── app.py              # Streamlit UI — inputs, layout, copy
├── finance.py          # Pure financial math, no UI dependencies
├── requirements.txt
├── tests/
│   └── test_finance.py # Unit tests for finance.py
└── README.md
```

The math is kept separate from the UI so it can be tested (and reused)
without spinning up Streamlit.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Running the tests

```bash
pytest
```

## Extension points (not built yet, on purpose)

The code leaves room for a few features without needing a rewrite:

- **Happiness score (1–10):** could soften the copy/framing of the output
  instead of purely scolding the user.
- **Calculation history:** logging each run to a local file or SQLite DB
  for later analysis, kept separate from the pure math in `finance.py`.

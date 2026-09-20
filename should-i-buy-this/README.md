# Should I Buy This? 💸

A small, playful calculator that shows the opportunity cost of a purchase —
what that money could be worth years from now if invested instead.

Not a guilt trip. Just math, with a chart.

## What it does

- Pick a purchase (name + price), mark it one-time or recurring
  (daily/weekly/monthly), set an assumed annual investment return and a
  time horizon.
- One-time purchases use simple compound growth: `FV = price * (1 + rate)^years`.
- Recurring purchases use the future value of a periodic annuity, so a
  $5 coffee habit compounds like a series of small investments rather
  than a single lump sum.
- Shows a headline number, a growth-curve chart, and a lighter secondary
  stat (e.g. what each coffee is "really" costing you).

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

- **Happiness score (1–10):** a slider that would soften the copy/framing
  of the output instead of purely scolding the user.
- **Calculation history:** logging each run to a local file or SQLite DB
  for later analysis, kept separate from the pure math in `finance.py`.
- **Custom portfolio rate:** a toggle to swap the flat assumed rate for a
  user-entered personal return — the math already just takes a plain
  `annual_rate` float, so this is a UI-only change when it's built.

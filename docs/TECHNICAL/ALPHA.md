# Alpha — Option Trading System

> **Module:** `alpha/` at the project root  
> **Package:** `stride-alytics-alpha`  
> **Python:** `>=3.11,<3.13`  
> **Package manager:** `uv` (or `pip` via `requirements.txt`)

---

## Overview

The **Alpha** module is a daily option screening and watchlist generation pipeline. It loads raw screener data from a CSV, computes option scores (0–9), assigns letter bands (A–E), applies daily entry filters, generates a weekly watchlist with strategy tags, inserts results into Supabase, and pushes them to Google Sheets.

A **Streamlit dashboard** provides a real-time view of the data stored in Supabase.

---

## Directory Structure

```
alpha/
├── utils/
│     ├── __init__.py
│     └── load_data.py              # Load & clean raw_screener.csv
├── screener/
│     ├── __init__.py
│     ├── compute_option_score.py   # Composite option score (0–9)
│     ├── apply_filters.py          # Daily entry filters + volatility bias
│     ├── weekly_watchlist.py       # Weekly watchlist with strategy tags
│     └── band_pipeline.py          # Letter band assignment (A–E)
├── database/
│     ├── __init__.py
│     ├── supabase_client.py        # Supabase client singleton
│     └── insert_daily.py           # Insert daily_metrics & option_scores
├── sheets/
│     ├── __init__.py
│     └── push_to_sheets.py         # Push DataFrames to Google Sheets
├── data_sources/
│     ├── __init__.py
│     ├── polygon.py                # Polygon.io option chain & aggregates
│     ├── yfinance_data.py          # Yahoo Finance stock data & options
│     └── fundamentals.py           # Financial Modeling Prep fundamentals
├── main.py                         # Pipeline orchestrator (run_system)
├── streamlit_app.py                # Streamlit dashboard
├── schema.sql                      # Supabase table definitions
├── pyproject.toml                  # uv/pip project config
├── requirements.txt                # pip dependencies (for GH Actions)
├── .env.example                    # Environment variable template
└── raw_screener.csv                # Input data (not committed)
```

---

## Pipeline Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ load_local_csv│──▶│compute_option│──▶│ compute_bands │──▶│apply_daily_  │
│ (raw_screener │   │   _score     │   │  (A–E bands)  │   │  filters     │
│   .csv)       │   │  (0–9 score) │   │               │   │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────┬───────┘
                                                                    │
                                                                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Push to     │◀───│  Insert into │◀───│  weekly_     │◀───│  (filtered   │
│  Google      │    │  Supabase    │    │  watchlist   │    │   daily)     │
│  Sheets      │    │  (daily_     │    │  (strategy   │    │              │
│  (3 sheets)  │    │   metrics +  │    │   tags)      │    │              │
│              │    │   scores)    │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Step-by-step

1. **Load** — `load_local_csv()` reads `raw_screener.csv`, parses dates, and coerces numeric columns.
2. **Score** — `compute_option_score()` assigns 0–9 based on 9 binary criteria (volume, OI, spread, IV, ATR, earnings, short interest, quality).
3. **Bands** — `compute_bands()` maps scores to letter bands: A (≥8), B (≥6), C (≥4), D (≥2), E (<2).
4. **Daily Filters** — `apply_daily_filters()` keeps only tickers passing all entry criteria and adds Volatility Bias & IV vs HV columns.
5. **Weekly Watchlist** — `weekly_watchlist()` filters for score ≥6 and assigns strategy tags based on IV rank and trend.
6. **Supabase** — `insert_daily_metrics()` and `insert_option_scores()` persist results.
7. **Google Sheets** — `push_to_sheet()` writes 3 worksheets: "Screener", "Daily Candidates", "Weekly Watchlist".

---

## Scoring Criteria (`compute_option_score.py`)

Each criterion adds 1 point to the score (max 9):

| # | Criterion                          | Condition                        |
|---|------------------------------------|----------------------------------|
| 1 | Option Volume                      | > 2,000                          |
| 2 | Max OI (Near Exp)                  | > 500                            |
| 3 | Bid-Ask Spread %                   | < 8%                             |
| 4 | IV 30d                             | > 0.25 (25%)                     |
| 5 | IV Rank (1y)                       | ≥ 40                             |
| 6 | ATR / Price                        | < 0.04 (4%)                      |
| 7 | Next Earnings Date                 | > 14 days away                   |
| 8 | Short Interest %                   | < 15%                            |
| 9 | Quality Score (1–5)                | ≥ 3                              |

---

## Band Assignment (`band_pipeline.py`)

| Score Range | Band |
|-------------|------|
| ≥ 8         | A    |
| ≥ 6         | B    |
| ≥ 4         | C    |
| ≥ 2         | D    |
| < 2         | E    |

---

## Daily Filters (`apply_filters.py`)

Tickers must pass ALL of:
- Option Volume ≥ 2,000
- Max OI (Near Exp) ≥ 500
- Bid-Ask Spread % ≤ 8
- Next Earnings Date > 14 days away
- Short Interest % < 15

Additional computed columns:
- **Volatility Bias**: "Sell Premium" (IV Rank ≥ 50), "Buy Premium" (IV Rank ≤ 30), "Neutral"
- **IV vs HV**: "IV > HV (Selling better)", "IV < HV (Buying better)", "IV ≈ HV"

---

## Strategy Tags (`weekly_watchlist.py`)

| IV Rank | Trend       | Strategy Tag                              |
|---------|-------------|-------------------------------------------|
| ≥ 50    | Bull        | Short Put / Bull Put Spread               |
| ≥ 50    | Bear        | Bear Call Spread / Iron Condor            |
| ≥ 50    | Other       | Iron Condor / Short Strangle              |
| ≤ 30    | Bull        | Bull Call Debit Spread / Call Calendar    |
| ≤ 30    | Bear        | Bear Put Debit Spread / Put Calendar      |
| ≤ 30    | Other       | Straddle / Strangle / Calendar            |
| 31–49   | Range       | Iron Condor / Butterfly                   |
| 31–49   | Other       | Directional Spread                        |

---

## CLI Usage

```bash
# Run the full pipeline
cd alpha
uv run python main.py

# Or with pip
pip install -r requirements.txt
python main.py
```

## Streamlit Dashboard

```bash
cd alpha
streamlit run streamlit_app.py
```

Opens a browser with 4 tabs:
- **Screener** — raw daily_metrics table
- **Bands & Scores** — option scores with line chart
- **Volatility** — IV vs HV comparison
- **Trades** — trade log with P&L bar chart

---

## Supabase Schema (`schema.sql`)

| Table            | Purpose                              |
|------------------|--------------------------------------|
| `symbols`        | Static ticker metadata               |
| `daily_metrics`  | Per-ticker per-day metrics           |
| `option_scores`  | Per-ticker per-day scores + band     |
| `signals`        | Buy/sell premium signals             |
| `trades`         | Trade log with P&L                   |
| `audit_log`      | Change tracking                      |

Run `schema.sql` in the Supabase SQL editor to create all tables.

---

## GitHub Actions

A scheduled workflow runs Mon–Fri at 12:30 UTC (≈ 8:30 AM ET):

```yaml
# .github/workflows/daily-option-system.yml
on:
  schedule:
    - cron: "30 12 * * 1-5"
```

Requires GitHub Secrets: `SUPABASE_URL`, `SUPABASE_KEY`.

---

## Environment Variables

| Variable       | Required | Description                        |
|----------------|----------|------------------------------------|
| `SUPABASE_URL` | Yes      | Supabase project URL               |
| `SUPABASE_KEY` | Yes      | Supabase service role key          |
| `POLYGON_API_KEY` | No   | Polygon.io API key                 |
| `FMP_API_KEY`  | No       | Financial Modeling Prep API key    |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to service account JSON |

Copy `.env.example` to `.env` and fill in values.

---

## Dependencies

| Package         | Purpose                        |
|-----------------|--------------------------------|
| `pandas`        | Data manipulation              |
| `python-dotenv` | Environment variable loading   |
| `supabase-py`   | Supabase client                |
| `gspread`       | Google Sheets API              |
| `google-auth`   | Google authentication          |
| `yfinance`      | Yahoo Finance data             |
| `requests`      | HTTP client (Polygon, FMP)     |
| `streamlit`     | Dashboard                      |
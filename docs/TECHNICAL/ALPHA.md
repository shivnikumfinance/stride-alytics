# Alpha — Option Trading System

> **Module:** `alpha/` at the project root  
> **Package:** `stride-alytics-alpha`  
> **Python:** `>=3.11,<3.13`  
> **Package manager:** `uv` (or `pip` via `requirements.txt`)

---

## Overview

The **Alpha** module is a daily option screening and watchlist generation pipeline. It loads raw screener data (today's Supabase rows, then `raw_screener.csv`), computes option scores (0–9), assigns letter bands (A–E), applies daily entry filters, generates a weekly watchlist with strategy tags, inserts results into Supabase, and pushes them to Google Sheets.

A **Streamlit dashboard** provides a real-time view of the data stored in Supabase.

---

## Directory Structure

```
alpha/
├── app/
│   ├── main.py                     # Pipeline orchestrator (run_system / main)
│   ├── streamlit_app.py            # Streamlit dashboard
│   ├── config.py                   # Environment config
│   ├── secrets_loader.py           # Required-key validator (not called by main)
│   ├── ingest.py                   # Multi-source ingestion (not wired into main yet)
│   ├── business_logic.py           # Unused duplicate of the scoring rules (see TODO)
│   ├── supabase_schema.sql         # Supabase table definitions
│   ├── utils/
│   │   ├── load_data.py            # Load Supabase / raw_screener.csv
│   │   ├── notify.py               # Slack/Discord alerts
│   │   └── date_utils.py
│   ├── screener/
│   │   ├── compute_option_score.py # Composite option score (0–9)
│   │   ├── band_pipeline.py        # Letter band assignment (A–E)
│   │   ├── apply_filters.py        # Daily entry filters + volatility bias
│   │   └── weekly_watchlist.py     # Weekly watchlist with strategy tags
│   ├── database/
│   │   ├── supabase_client.py      # Supabase client singleton
│   │   └── insert_daily.py         # replace_day + insert helpers
│   ├── sheets/push_to_sheets.py    # Push DataFrames to Google Sheets
│   └── data_sources/               # polygon, yfinance_data, fmp_fundamentals, massive, ticker_universe
├── tests/                          # pytest (fake Supabase client, no network)
├── scripts/                        # uv run lint | format | typecheck | test | verify
├── raw_screener.csv                # Manual input fallback (tracked in git)
├── .env.example                    # Environment template (local, not tracked)
└── pyproject.toml                  # uv project config
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

1. **Load** — `load_from_supabase()` reads today's `daily_metrics` rows; if there are none, `load_local_csv()` reads `raw_screener.csv` (parses dates, coerces numbers). If neither has data the run **fails** (see Failure policy).
2. **Score** — `compute_option_score()` assigns 0–9 based on 9 binary criteria (volume, OI, spread, IV, ATR, earnings, short interest, quality).
3. **Bands** — `compute_bands()` maps scores to letter bands: A (≥8), B (≥6), C (≥4), D (≥2), E (<2).
4. **Daily Filters** — `apply_daily_filters()` keeps only tickers passing all entry criteria and adds Volatility Bias & IV vs HV columns.
5. **Weekly Watchlist** — `weekly_watchlist()` filters for score ≥6 and assigns strategy tags based on IV rank and trend.
6. **Supabase** — `replace_day()` replaces today's rows in `daily_metrics`, `option_scores`, `bands` and `weekly_watchlist`. Payloads are built before anything is deleted; deletes match `date LIKE 'YYYY-MM-DD%'`; errors are raised.
7. **Google Sheets** — only if `GOOGLE_SHEETS_SPREADSHEET_ID` is set: `push_to_sheet()` writes 3 worksheets: "Screener", "Daily Candidates", "Weekly Watchlist".

### Failure policy

- **No real data → the run fails** (non-zero exit). Built-in demo rows are used only with `ALLOW_SAMPLE_DATA=1` and are never written to Supabase or Google Sheets.
- **A Supabase write failure fails the run.** `main()` returns exit code 1.
- **A Google Sheets failure** is reported as an alert but does not fail the run.
- **Alerts** go to `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL` when set (`app/utils/notify.py`); if neither is set the alert is only printed.
- **Stale CSV:** if the CSV fallback is older than `MAX_CSV_AGE_DAYS` (default 3) a warning and alert are sent, because its values would be stamped with today's date.

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
# Run the full pipeline (exit code 1 + alert on failure)
cd alpha
uv sync
uv run python app/main.py

# Local demo without real data (never written to Supabase)
ALLOW_SAMPLE_DATA=1 uv run python app/main.py

# Tests
uv run pytest tests -q
```

## Streamlit Dashboard

```bash
cd alpha
uv run streamlit run app/streamlit_app.py
```

Run it from `alpha/` so the `app.*` imports resolve. It shows the **latest day only** (paged past the 1000-row API limit) in 4 tabs:
- **Screener** — daily_metrics table
- **Bands & Scores** — option scores table
- **Volatility** — IV vs HV table
- **Trades** — empty placeholder (no trade data is loaded yet)

> The dashboard uses the Supabase service-role key and has no login. Keep the app private.

---

## Supabase Schema (`app/supabase_schema.sql`)

| Table              | Purpose                                         |
|--------------------|-------------------------------------------------|
| `daily_metrics`    | Per-ticker per-day metrics (one snapshot a day) |
| `option_scores`    | Per-ticker per-day scores, trend, strategy      |
| `bands`            | Per-ticker per-day band (A–E)                   |
| `weekly_watchlist` | Weekly watchlist with strategy tags             |
| `trades`           | Trade log (not written by the pipeline yet)     |
| `audit_log`        | Change tracking (not written yet)               |

Every `date` column is TEXT holding `YYYY-MM-DD`. Run `app/supabase_schema.sql` in the Supabase SQL editor to create the tables.

---

## GitHub Actions

A scheduled workflow runs Mon–Fri at 12:30 UTC (≈ 8:30 AM ET):

```yaml
# .github/workflows/daily_run.yml
on:
  schedule:
    - cron: "30 12 * * 1-5"   # UTC: 8:30 AM EDT / 7:30 AM EST
```

It runs `uv run python app/main.py` (not plain `python`, which would not see the project's dependencies) and passes secrets as environment variables.

Required GitHub secrets: `SUPABASE_URL`, `SUPABASE_KEY`.
Optional: `GOOGLE_SERVICE_ACCOUNT_JSON`, `GOOGLE_SHEETS_SPREADSHEET_ID`, `SLACK_WEBHOOK_URL`, `DISCORD_WEBHOOK_URL`.

Note: the workflow does not run ingestion, so today's data must already be in Supabase or in `raw_screener.csv`.

---

## Environment Variables

| Variable       | Required | Description                        |
|----------------|----------|------------------------------------|
| `SUPABASE_URL` | Yes      | Supabase project URL               |
| `SUPABASE_KEY` | Yes      | Supabase service role key          |
| `POLYGON_API_KEY` | Ingestion only | Polygon.io API key         |
| `FMP_API_KEY`  | Ingestion only | Financial Modeling Prep API key |
| `MASSIVE_API_KEY` | No    | Optional extra data source         |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | No | Service-account JSON (or place `service_account.json` in `alpha/`) |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | No | Target spreadsheet; Sheets push is skipped if unset |
| `SLACK_WEBHOOK_URL` / `DISCORD_WEBHOOK_URL` | No | Failure/warning alerts |
| `ALLOW_SAMPLE_DATA` | No  | `1` = allow demo rows when there is no data (never saved) |
| `MAX_CSV_AGE_DAYS` | No   | Warn when the CSV fallback is older than this (default 3) |

Create `alpha/.env` from your own values (a local `.env.example` template is not tracked in git).

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
| `requests`      | HTTP client (Polygon, FMP, alert webhooks) |
| `streamlit`     | Dashboard                      |
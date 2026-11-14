"""
Alpha — StrideAlytics Option Trading System Pipeline.

Orchestrates: load data (DB or CSV) → score options → compute bands → apply filters →
generate watchlist → insert into Supabase → push to Google Sheets.

Failure policy
--------------
* No real data (Supabase empty for today AND no CSV): the run FAILS. Built-in demo
  rows are used only if explicitly allowed (``ALLOW_SAMPLE_DATA=1``) and are never
  written to Supabase or Google Sheets.
* A Supabase write failure FAILS the run (non-zero exit + alert).
* A Google Sheets failure is reported as an alert but does not fail the run.
* ``SLACK_WEBHOOK_URL`` / ``DISCORD_WEBHOOK_URL`` receive failure/warning alerts.
"""

import os
import time

import pandas as pd

from app.utils.load_data import load_from_supabase, load_local_csv
from app.utils.notify import send_alert
from app.screener.compute_option_score import compute_option_score
from app.screener.apply_filters import apply_daily_filters
from app.screener.weekly_watchlist import weekly_watchlist, compute_strategy_for_all
from app.screener.band_pipeline import compute_bands
from app.database.insert_daily import replace_day
from app.sheets.push_to_sheets import push_to_sheet

# Warn when the CSV fallback is older than this many days (its values would be
# stamped with today's date even though they are old).
MAX_CSV_AGE_DAYS = int(os.getenv("MAX_CSV_AGE_DAYS", "3"))

CSV_COLUMNS = [
    "Ticker",
    "Price",
    "Avg Volume (Shares)",
    "Option Volume",
    "Max OI (Near Exp)",
    "Bid-Ask Spread %",
    "IV 30d",
    "IV Rank (1y)",
    "HV 30d",
    "ATR",
    "Next Earnings Date",
    "Short Interest %",
    "Revenue Growth (YoY)",
    "Debt/Equity",
    "Quality Score (1-5)",
    "Trend (Above/Below 20/50/200 EMA)",
    "Sector",
]


class NoDataError(RuntimeError):
    """No real input data was available for today's run."""


def _sample_data() -> pd.DataFrame:
    """Demo rows for local experiments. NOT market data; earnings dates are relative to today."""

    def soon(days: int) -> str:
        return (pd.Timestamp.today() + pd.Timedelta(days=days)).strftime("%Y-%m-%d")

    rows = [
        ["AAPL", 190.50, 45000000, 5000, 1200, 3.5, 0.35, 65, 0.25, 2.5, soon(40), 1.2, 0.12, 1.3, 5,
         "Above 20, 50, 200 (Bullish)", "Technology"],
        ["MSFT", 330.25, 25000000, 3500, 800, 2.0, 0.28, 45, 0.22, 4.2, soon(50), 0.8, 0.18, 0.4, 5,
         "Above 20, 50, 200 (Bullish)", "Technology"],
        ["GOOGL", 140.80, 18000000, 4200, 600, 4.5, 0.32, 55, 0.30, 3.8, soon(60), 1.0, 0.08, 0.2, 4,
         "Above 20, Below 50, Above 200", "Technology"],
        ["TSLA", 250.40, 90000000, 15000, 2500, 6.0, 0.65, 80, 0.55, 12.0, soon(35), 2.5, -0.05, 0.8, 3,
         "Below 20, 50, 200 (Bearish)", "Consumer Cyclical"],
        ["NVDA", 850.30, 45000000, 8500, 1800, 3.0, 0.45, 70, 0.38, 15.0, soon(45), 1.5, 0.55, 0.1, 5,
         "Above 20, 50, 200 (Bullish)", "Technology"],
    ]  # fmt: skip
    df = pd.DataFrame(rows, columns=CSV_COLUMNS)
    df["Next Earnings Date"] = pd.to_datetime(df["Next Earnings Date"])
    return df


def _load_data(allow_sample: bool) -> tuple[str, pd.DataFrame]:
    """Return ``(source, df)`` with source in {'supabase', 'csv', 'sample'}."""
    print("Loading data from Supabase...")
    df = load_from_supabase()
    if not df.empty:
        return "supabase", df

    print("No data in Supabase for today, trying local CSV...")
    df = load_local_csv()
    if not df.empty:
        path = df.attrs.get("source_path")
        if path and os.path.exists(path):
            age_days = (time.time() - os.path.getmtime(path)) / 86400
            if age_days > MAX_CSV_AGE_DAYS:
                msg = (
                    f"[WARNING] {path} is {age_days:.0f} days old; today's run will stamp its "
                    "values with today's date. Refresh the CSV or wire up ingestion."
                )
                print(msg)
                send_alert(f"Alpha: CSV fallback is stale ({age_days:.0f} days old).")
        return "csv", df

    if allow_sample:
        print("[WARNING] No real data found; using built-in SAMPLE data (will not be saved).")
        return "sample", _sample_data()

    raise NoDataError(
        "No input data: Supabase has no rows for today and no raw_screener.csv was found. "
        "Refusing to fabricate data. (Set ALLOW_SAMPLE_DATA=1 for a local demo run.)"
    )


def run_system(allow_sample: bool | None = None) -> None:
    """Run the full daily option screening pipeline. Raises on failure."""
    if allow_sample is None:
        allow_sample = os.getenv("ALLOW_SAMPLE_DATA") == "1"

    # 1. Load raw data — Supabase first, then CSV, then (opt-in only) sample data
    source, df = _load_data(allow_sample)
    print(f"Loaded {len(df)} rows from {source}")

    # 2. Score options
    print("\nScoring options...")
    df_scored = compute_option_score(df)

    # 3. Compute bands
    print("Computing bands...")
    df_bands = compute_bands(df_scored)

    # 4. Compute strategy for all tickers (needed for option_scores table)
    print("Computing strategy tags...")
    df_bands = compute_strategy_for_all(df_bands)

    # 5. Apply daily filters
    print("Applying daily filters...")
    daily = apply_daily_filters(df_bands)

    # 6. Generate weekly watchlist
    print("Generating weekly watchlist...")
    weekly = weekly_watchlist(df_bands)

    if df_bands.empty:
        raise NoDataError("Pipeline produced no rows after scoring.")

    if source == "sample":
        print("Sample data: skipping Supabase and Google Sheets writes.")
        return

    # 7. Replace today's rows in Supabase. Errors propagate (non-zero exit + alert).
    print("Writing data to Supabase...")
    counts = replace_day(df_bands, weekly)
    print(f"Supabase updated: {counts}")

    # 8. Push to Google Sheets (only if configured). Failures alert but don't fail the run.
    if not os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID"):
        print("Google Sheets not configured (GOOGLE_SHEETS_SPREADSHEET_ID unset) — skipping.")
    elif daily.empty:
        print("No candidates passed the daily filters — skipping Google Sheets.")
    else:
        print("Pushing to Google Sheets...")
        try:
            push_to_sheet(df_bands, "Screener")
            push_to_sheet(daily, "Daily Candidates")
            push_to_sheet(weekly, "Weekly Watchlist")
        except Exception as e:
            print(f"[WARNING] Google Sheets push failed: {e}")
            send_alert(f"Alpha: Google Sheets push failed: {e}")


def main() -> int:
    """CLI entry point: returns a non-zero exit code (and alerts) on failure."""
    try:
        run_system()
    except Exception as e:  # noqa: BLE001 - top-level handler: report everything
        print(f"[ERROR] Alpha daily run failed: {e}")
        send_alert(f"Alpha daily run FAILED: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

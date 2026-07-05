"""
Alpha — StrideAlytics Option Trading System Pipeline.

Orchestrates: load CSV → score options → compute bands → apply filters →
generate watchlist → insert into Supabase → push to Google Sheets.
"""

import pandas as pd
from app.utils.load_data import load_local_csv
from app.screener.compute_option_score import compute_option_score
from app.screener.apply_filters import apply_daily_filters
from app.screener.weekly_watchlist import weekly_watchlist
from app.screener.band_pipeline import compute_bands
from app.database.insert_daily import (
    insert_daily_metrics,
    insert_option_scores,
    insert_bands,
    insert_weekly_watchlist,
)
from app.sheets.push_to_sheets import push_to_sheet


def run_system() -> None:
    """Run the full daily option screening pipeline."""
    # Define column names from CSV
    csv_columns = [
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
        "Quality Score (1–5)",
        "Trend (Above/Below 20/50/200 EMA)",
    ]

    # 1. Load raw data
    df = load_local_csv()

    # If empty, create sample data for demonstration
    if df.empty:
        print("Note: raw_screener.csv is empty, using sample data for demonstration...")
        df = pd.DataFrame(
            [
                [
                    "AAPL",
                    190.50,
                    45000000,
                    5000,
                    1200,
                    3.5,
                    0.35,
                    65,
                    0.25,
                    2.5,
                    "2026-07-28",
                    1.2,
                    0.12,
                    1.3,
                    5,
                    "Above 20, 50, 200 (Bullish)",
                ],
                [
                    "MSFT",
                    330.25,
                    25000000,
                    3500,
                    800,
                    2.0,
                    0.28,
                    45,
                    0.22,
                    4.2,
                    "2026-08-05",
                    0.8,
                    0.18,
                    0.4,
                    5,
                    "Above 20, 50, 200 (Bullish)",
                ],
                [
                    "GOOGL",
                    140.80,
                    18000000,
                    4200,
                    600,
                    4.5,
                    0.32,
                    55,
                    0.30,
                    3.8,
                    "2026-08-30",
                    1.0,
                    0.08,
                    0.2,
                    4,
                    "Above 20, Below 50, Above 200",
                ],
                [
                    "TSLA",
                    250.40,
                    90000000,
                    15000,
                    2500,
                    6.0,
                    0.65,
                    80,
                    0.55,
                    12.0,
                    "2026-08-15",
                    2.5,
                    -0.05,
                    0.8,
                    3,
                    "Below 20, 50, 200 (Bearish)",
                ],
                [
                    "NVDA",
                    850.30,
                    45000000,
                    8500,
                    1800,
                    3.0,
                    0.45,
                    70,
                    0.38,
                    15.0,
                    "2026-08-20",
                    1.5,
                    0.55,
                    0.1,
                    5,
                    "Above 20, 50, 200 (Bullish)",
                ],
            ],
            columns=csv_columns,
        )
        df["Next Earnings Date"] = pd.to_datetime(df["Next Earnings Date"])

    # 2. Score options
    df_scored = compute_option_score(df)

    # 3. Compute bands
    df_bands = compute_bands(df_scored)

    # 4. Apply daily filters
    daily = apply_daily_filters(df_bands)

    # 5. Generate weekly watchlist
    weekly = weekly_watchlist(df_bands)

    # 6. Insert into Supabase (skip if no real data or tables don't exist)
    if not df_bands.empty:
        print("Inserting data into Supabase...")
        try:
            insert_daily_metrics(df_bands)
            insert_bands(df_bands)
            insert_option_scores(df_bands)
            insert_weekly_watchlist(weekly)
        except Exception as e:
            print(f"[WARNING] Supabase insert failed (table may not exist): {e}")

    # 7. Push to Google Sheets (skip if no real data)
    if not df_bands.empty and not daily.empty:
        print("Pushing to Google Sheets...")
        try:
            push_to_sheet(df_bands, "Screener")
            push_to_sheet(daily, "Daily Candidates")
            push_to_sheet(weekly, "Weekly Watchlist")
        except Exception as e:
            print(f"[WARNING] Google Sheets push failed: {e}")


if __name__ == "__main__":
    run_system()

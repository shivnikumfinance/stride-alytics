"""
Alpha — StrideAlytics Option Trading System Pipeline.

Orchestrates: load data (DB or CSV) → score options → compute bands → apply filters →
generate watchlist → insert into Supabase → push to Google Sheets.
"""

import pandas as pd

from app.utils.load_data import load_from_supabase, load_local_csv
from app.screener.compute_option_score import compute_option_score
from app.screener.apply_filters import apply_daily_filters
from app.screener.weekly_watchlist import weekly_watchlist, compute_strategy_for_all
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
    # Define column names from CSV (used if fallback needed)
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
        "Quality Score (1-5)",
        "Trend (Above/Below 20/50/200 EMA)",
        "Sector",
    ]

    # 1. Load raw data - PRIORITY: Supabase DB first, then CSV, then sample data
    print("Loading data from Supabase...")
    df = load_from_supabase()
    
    if df.empty:
        print("No data in Supabase, trying local CSV...")
        df = load_local_csv()
    
    if df.empty:
        print("No CSV data found, using sample data for demonstration...")
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
                    "Technology",
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
                    "Technology",
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
                    "Technology",
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
                    "Consumer Cyclical",
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
                    "Technology",
                ],
            ],
            columns=csv_columns,
        )
        df["Next Earnings Date"] = pd.to_datetime(df["Next Earnings Date"])

    print(f"Loaded {len(df)} rows")

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

    # 7. Insert into Supabase (clear old data first to avoid duplicates)
    if not df_bands.empty:
        print("Inserting data into Supabase...")
        try:
            # Clear existing data for today before inserting
            today_str = pd.Timestamp.today().strftime("%Y-%m-%d")
            from app.database.supabase_client import get_supabase_client
            client = get_supabase_client()
            try:
                client.table("daily_metrics").delete().eq("date", today_str).execute()
                client.table("option_scores").delete().eq("date", today_str).execute()
                client.table("bands").delete().eq("date", today_str).execute()
                client.table("weekly_watchlist").delete().eq("date", today_str).execute()
            except Exception:
                pass  # Tables may not exist yet
            
            insert_daily_metrics(df_bands)
            insert_bands(df_bands)
            insert_option_scores(df_bands)
            insert_weekly_watchlist(weekly)
        except Exception as e:
            print(f"[WARNING] Supabase insert failed (table may not exist): {e}")

    # 8. Push to Google Sheets (skip if no real data)
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
"""
Local test script for the Alpha pipeline.
Tests core functionality (loading, scoring, bands, filters) without external services.
"""
import pandas as pd
from app.utils.load_data import load_local_csv
from app.screener.compute_option_score import compute_option_score
from app.screener.band_pipeline import compute_bands
from app.screener.apply_filters import apply_daily_filters
from app.screener.weekly_watchlist import weekly_watchlist, compute_strategy_for_all


def run_local_test() -> None:
    """Run the core pipeline steps that don't require external services."""
    # Define sample data columns
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

    # 1. Load raw data
    print("Loading raw screener data...")
    df = load_local_csv()
    print(f"Loaded {len(df)} rows")

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

    # 2. Score options
    print("\nScoring options...")
    df_scored = compute_option_score(df)

    # 3. Compute bands
    print("Computing bands...")
    df_bands = compute_bands(df_scored)

    # 4. Compute strategy for all tickers
    print("Computing strategy tags...")
    df_bands = compute_strategy_for_all(df_bands)

    # 5. Apply daily filters
    print("Applying daily filters...")
    daily = apply_daily_filters(df_bands)

    # 6. Generate weekly watchlist
    print("Generating weekly watchlist...")
    weekly = weekly_watchlist(df_bands)

    # Display results
    print("\n" + "=" * 60)
    print("SCREENER RESULTS (all rows with scores):")
    print("=" * 60)
    print(df_bands[["Ticker", "Price", "Option Score", "Band", "Strategy Tag", "Sector"]].to_string(index=False))

    print("\n" + "=" * 60)
    print("DAILY CANDIDATES (after filters):")
    print("=" * 60)
    if not daily.empty:
        print(daily[["Ticker", "Price", "Option Score", "Band", "Volatility Bias", "IV vs HV", "Sector", "Strategy Tag"]].to_string(index=False))
    else:
        print("No daily candidates match all criteria.")

    print("\n" + "=" * 60)
    print("WEEKLY WATCHLIST:")
    print("=" * 60)
    if not weekly.empty:
        print(weekly[["Ticker", "Date", "Sector", "Price", "Option Score", "IV Rank (1y)", "Strategy Tag"]].to_string(index=False))
    else:
        print("No weekly watchlist candidates match criteria.")

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    run_local_test()
"""
Alpha — StrideAlytics Option Trading System Pipeline.

Orchestrates: load CSV → score options → compute bands → apply filters →
generate watchlist → insert into Supabase → push to Google Sheets.
"""

from app.utils.load_data import load_local_csv
from app.screener.compute_option_score import compute_option_score
from app.screener.apply_filters import apply_daily_filters
from app.screener.weekly_watchlist import weekly_watchlist
from app.screener.band_pipeline import compute_bands
from app.database.insert_daily import insert_daily_metrics, insert_option_scores
from app.sheets.push_to_sheets import push_to_sheet


def run_system() -> None:
    """Run the full daily option screening pipeline."""
    # 1. Load raw data
    df = load_local_csv()

    # 2. Score options
    df_scored = compute_option_score(df)

    # 3. Compute bands
    df_bands = compute_bands(df_scored)

    # 4. Apply daily filters
    daily = apply_daily_filters(df_bands)

    # 5. Generate weekly watchlist
    weekly = weekly_watchlist(df_bands)

    # 6. Insert into Supabase
    insert_daily_metrics(df_bands)
    insert_option_scores(df_bands)

    # 7. Push to Google Sheets
    push_to_sheet(df_bands, "Screener")
    push_to_sheet(daily, "Daily Candidates")
    push_to_sheet(weekly, "Weekly Watchlist")


if __name__ == "__main__":
    run_system()
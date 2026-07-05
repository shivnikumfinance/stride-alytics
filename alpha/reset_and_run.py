"""
Reset script to clear Supabase tables and re-run the pipeline.
Use this when data appears corrupted or wrong.
"""
import pandas as pd
from app.database.supabase_client import get_supabase_client

def clear_tables():
    """Clear ALL data from the screener tables (not just today's)."""
    client = get_supabase_client()
    try:
        # Delete ALL rows using a condition that matches everything
        client.table("daily_metrics").delete().neq("ticker", "NEVER_MATCH").execute()
        client.table("option_scores").delete().neq("ticker", "NEVER_MATCH").execute()
        client.table("bands").delete().neq("ticker", "NEVER_MATCH").execute()
        client.table("weekly_watchlist").delete().neq("ticker", "NEVER_MATCH").execute()
        print("[OK] All tables cleared successfully")
    except Exception as e:
        print(f"[WARNING] Could not clear tables: {e}")

def run_pipeline():
    """Run the main pipeline to populate tables with correct data."""
    from app.main import run_system
    run_system()

if __name__ == "__main__":
    print("Clearing Supabase tables...")
    clear_tables()
    print("\nRunning pipeline...")
    run_pipeline()
    print("\nDone!")
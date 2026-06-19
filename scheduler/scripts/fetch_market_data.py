"""
Fetch daily market data from yfinance and store in Supabase.
Scheduled: Mon-Fri @ 3:00 PM EST (20:00 UTC)
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def main():
    print(f"Fetching market data from yfinance...")
    url = f"{SUPABASE_URL}/rest/v1/rpc/fetch_market_data"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    print("✓ Market data fetch complete (placeholder)")


if __name__ == "__main__":
    main()
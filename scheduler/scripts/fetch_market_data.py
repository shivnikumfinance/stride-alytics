"""
Fetch daily market data from yfinance and store in Supabase.
Scheduled: Mon-Fri @ 3:00 PM EST (20:00 UTC)

Phase 2 implementation: fetches real option chain data via yfinance for all
tracked symbols and upserts results into the Supabase ``options`` table.
"""

import os
import sys
import asyncio
from datetime import date

from dotenv import load_dotenv

# Add backend to path so we can reuse services
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Tracked symbols — same list as in backend/app/services/screener.py
TRACKED_SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "AMD"]


async def fetch_and_cache_all():
    """Fetch option chains for all tracked symbols and upsert into Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("✗ SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    from app.services.screener import fetch_and_cache_supabase

    print(f"🚀 Fetching market data for {len(TRACKED_SYMBOLS)} symbols...")
    success_count = 0

    for symbol in TRACKED_SYMBOLS:
        print(f"  → Fetching {symbol}...")
        try:
            result = await fetch_and_cache_supabase(symbol, SUPABASE_URL, SUPABASE_KEY)
            if result:
                success_count += 1
                print(f"    ✓ {symbol} cached successfully")
            else:
                print(f"    ✗ {symbol} failed — no data returned")
        except Exception as e:
            print(f"    ✗ {symbol} error: {e}")

    print(f"\n✓ Done. Successfully cached {success_count}/{len(TRACKED_SYMBOLS)} symbols to Supabase")
    print(f"  Date: {date.today().isoformat()}")
    print(f"  Supabase URL: {SUPABASE_URL[:30]}...")


def main():
    asyncio.run(fetch_and_cache_all())


if __name__ == "__main__":
    main()
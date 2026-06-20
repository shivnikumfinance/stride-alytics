"""
Calculate option Greeks for tracked symbols and store in Supabase.
Scheduled: Mon-Fri @ 4:00 PM EST (21:00 UTC)

Phase 2 implementation: reads option chain data from Supabase, recalculates
Greeks using the Black-Scholes engine, and updates the records.
"""

import os
import sys
from datetime import date

import httpx
from dotenv import load_dotenv

# Add backend to path so we can reuse the Greeks engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Tracked symbols
TRACKED_SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "AMD"]


def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("✗ SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    from app.services.greeks import calculate_greeks

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    print(f"🚀 Calculating Greeks for {len(TRACKED_SYMBOLS)} symbols...")
    total_updated = 0

    for symbol in TRACKED_SYMBOLS:
        try:
            # Fetch current options data from Supabase for this symbol
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    f"{SUPABASE_URL}/rest/v1/options",
                    headers=headers,
                    params={
                        "symbol": f"eq.{symbol}",
                        "select": "symbol,strike,expiry,option_type,implied_vol,last_price",
                        "limit": 200,
                    },
                )

                if resp.status_code != 200 or not resp.json():
                    print(f"  → {symbol}: no data in Supabase (yet)")
                    continue

                options = resp.json()
                print(f"  → {symbol}: processing {len(options)} contracts...")

                updated_count = 0
                for opt in options:
                    try:
                        strike = float(opt.get("strike", 0))
                        iv = float(opt.get("implied_vol", 0.3))
                        last_price = float(opt.get("last_price", 0))

                        if strike <= 0:
                            continue

                        time_to_expiry_days = (date.fromisoformat(opt["expiry"]) - date.today()).days
                        if time_to_expiry_days <= 0:
                            continue

                        time_to_expiry = time_to_expiry_days / 365.0

                        # Calculate Greeks using the shared engine
                        greeks = calculate_greeks(
                            spot=last_price or strike,
                            strike=strike,
                            time_to_expiry=time_to_expiry,
                            volatility=iv,
                            option_type=opt["option_type"],
                        )

                        # Update the record in Supabase
                        update_payload = {
                            "delta": greeks.delta,
                            "gamma": greeks.gamma,
                            "theta": greeks.theta,
                            "vega": greeks.vega,
                            "rho": greeks.rho,
                            "updated_at": date.today().isoformat(),
                        }

                        update_resp = client.patch(
                            f"{SUPABASE_URL}/rest/v1/options",
                            headers={**headers, "Prefer": "return=minimal"},
                            params={
                                "symbol": f"eq.{opt['symbol']}",
                                "strike": f"eq.{opt['strike']}",
                                "expiry": f"eq.{opt['expiry']}",
                                "option_type": f"eq.{opt['option_type']}",
                            },
                            json=update_payload,
                        )

                        if update_resp.status_code < 400:
                            updated_count += 1

                    except Exception as e:
                        print(f"    ⚠️ Error processing {opt.get('symbol', '?')} {opt.get('strike', '?')}: {e}")
                        continue

                total_updated += updated_count
                print(f"    ✓ Updated {updated_count} contracts for {symbol}")

        except Exception as exc:
            print(f"    ✗ {symbol} error: {exc}")
            continue

    print(f"\n✓ Done. Calculated/updated Greeks for {total_updated} contracts across {len(TRACKED_SYMBOLS)} symbols")
    print(f"  Date: {date.today().isoformat()}")


if __name__ == "__main__":
    main()
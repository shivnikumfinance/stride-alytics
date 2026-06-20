"""
Generate weekly options picks based on technical analysis.
Scheduled: Sundays @ 6:00 PM EST (23:00 UTC)

Phase 2 implementation: uses yfinance to analyze market data for tracked
symbols, scores potential trades based on technical indicators, and
inserts the top picks into the Supabase ``weekly_picks`` table.
"""

import os
import sys
import math
from datetime import date, timedelta

import httpx
import yfinance as yf
from dotenv import load_dotenv

# Add backend to path so we can reuse constants
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# Symbols to analyze for weekly picks
ANALYSIS_SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "AMD"]


def calculate_sma(prices: list[float], period: int) -> list[float | None]:
    """Calculate Simple Moving Average."""
    if len(prices) < period:
        return [None] * len(prices)
    result: list[float | None] = [None] * (period - 1)
    for i in range(period - 1, len(prices)):
        result.append(sum(prices[i - period + 1 : i + 1]) / period)
    return result


def calculate_rsi(prices: list[float], period: int = 14) -> list[float | None]:
    """Calculate Relative Strength Index."""
    if len(prices) < period + 1:
        return [None] * len(prices)
    result: list[float | None] = [None] * period
    gains = []
    losses = []
    for i in range(1, period + 1):
        diff = prices[i] - prices[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    for i in range(period, len(prices)):
        diff = prices[i] - prices[i - 1]
        gain = max(diff, 0)
        loss = max(-diff, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            result.append(100.0)
        else:
            rs = avg_gain / avg_loss
            result.append(100.0 - 100.0 / (1 + rs))
    return result


def analyze_symbol(symbol: str) -> dict | None:
    """Analyze a symbol and return a trade pick with confidence score."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="3mo")

        if hist.empty or len(hist) < 30:
            return None

        closes = [float(c) for c in hist["Close"].tolist()]
        current_price = closes[-1]
        sma_20 = calculate_sma(closes, 20)
        sma_50 = calculate_sma(closes, 50)
        rsi = calculate_rsi(closes)

        last_sma20 = sma_20[-1] if sma_20[-1] is not None else current_price
        last_sma50 = sma_50[-1] if sma_50[-1] is not None else current_price
        last_rsi = rsi[-1] if rsi[-1] is not None else 50.0

        # Scoring logic
        score = 0.0
        signals = []

        # Trend following
        if current_price > last_sma20:
            score += 0.2
            signals.append("above_20_sma")
        if current_price > last_sma50:
            score += 0.2
            signals.append("above_50_sma")
        if last_sma20 > last_sma50:
            score += 0.15
            signals.append("golden_cross")

        # RSI signals
        if last_rsi < 30:
            score += 0.2
            signals.append("oversold")
        elif last_rsi > 70:
            score -= 0.1
            signals.append("overbought")

        # Momentum
        returns_5d = (closes[-1] - closes[-5]) / closes[-5] if len(closes) >= 5 else 0
        returns_20d = (closes[-1] - closes[-20]) / closes[-20] if len(closes) >= 20 else 0

        if returns_5d > 0 and returns_20d > 0:
            score += 0.15
            signals.append("momentum_up")
        elif returns_5d < -0.02:
            score -= 0.1
            signals.append("momentum_down")

        # Volatility (use high-low range as proxy)
        recent_high = max(closes[-20:]) if len(closes) >= 20 else current_price * 1.05
        recent_low = min(closes[-20:]) if len(closes) >= 20 else current_price * 0.95
        range_pct = (recent_high - recent_low) / current_price

        # Determine direction and side
        side = "call" if score > 0.3 else "put"
        direction_label = "bullish" if side == "call" else "bearish"

        # Set strike targets based on current price
        if side == "call":
            strike = round(current_price * 1.02, 2)  # Slightly OTM
            target = round(current_price * 1.05, 2)
            stop = round(current_price * 0.97, 2)
        else:
            strike = round(current_price * 0.98, 2)
            target = round(current_price * 0.95, 2)
            stop = round(current_price * 1.03, 2)

        # Next weekly expiry (Friday)
        today = date.today()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7  # Next Friday
        expiry = today + timedelta(days=days_until_friday)

        # Build rationale
        rationale_parts = []
        if "above_50_sma" in signals:
            rationale_parts.append("above 50-day SMA")
        if "golden_cross" in signals:
            rationale_parts.append("20/50 SMA golden cross")
        if "oversold" in signals:
            rationale_parts.append(f"RSI oversold ({last_rsi:.0f})")
        if "momentum_up" in signals:
            rationale_parts.append("positive momentum")
        rationale = f"{direction_label.capitalize()} bias: {', '.join(rationale_parts) if rationale_parts else 'neutral setup'}"

        return {
            "symbol": symbol,
            "side": side,
            "strike": strike,
            "expiry": expiry.isoformat(),
            "entry_price": round(current_price, 2),
            "target_price": round(target, 2),
            "stop_loss": round(stop, 2),
            "rationale": rationale,
            "confidence": round(min(1.0, max(0.1, score)), 2),
            "current_price": round(current_price, 2),
            "rsi": round(last_rsi, 1),
            "range_pct": round(range_pct * 100, 1),
        }

    except Exception as exc:
        print(f"    ✗ Error analyzing {symbol}: {exc}")
        return None


def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("✗ SUPABASE_URL and SUPABASE_KEY must be set")
        sys.exit(1)

    print(f"🚀 Generating weekly picks for {len(ANALYSIS_SYMBOLS)} symbols...")
    picks = []

    for symbol in ANALYSIS_SYMBOLS:
        print(f"  → Analyzing {symbol}...")
        result = analyze_symbol(symbol)
        if result:
            picks.append(result)
            print(f"    ✓ {symbol}: {result['side'].upper()} @ {result['strike']} (confidence: {result['confidence']})")
        else:
            print(f"    ⚠️ {symbol}: insufficient data")

    # Sort by confidence descending and take top 5-7
    picks.sort(key=lambda p: p["confidence"], reverse=True)
    top_picks = picks[:6]

    # Calculate the Monday of the current week for week_of
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_of = monday.isoformat()

    print(f"\n📊 Top {len(top_picks)} picks for week of {week_of}:")
    for i, pick in enumerate(top_picks, 1):
        print(f"  {i}. {pick['symbol']} {pick['side']} @ ${pick['strike']} (score: {pick['confidence']})")

    # Upsert into Supabase weekly_picks table
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    inserted = 0
    for pick in top_picks:
        payload = {
            "symbol": pick["symbol"],
            "side": pick["side"],
            "strike": pick["strike"],
            "expiry": pick["expiry"],
            "entry_price": pick["entry_price"],
            "target_price": pick["target_price"],
            "stop_loss": pick["stop_loss"],
            "rationale": pick["rationale"],
            "confidence": pick["confidence"],
            "week_of": week_of,
        }

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{SUPABASE_URL}/rest/v1/weekly_picks",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code < 400:
                    inserted += 1
                else:
                    print(f"    ⚠️ Supabase insert failed for {pick['symbol']}: {resp.status_code} {resp.text[:100]}")
        except Exception as exc:
            print(f"    ✗ Supabase error for {pick['symbol']}: {exc}")

    print(f"\n✓ Done. Published {inserted} weekly picks to Supabase")
    print(f"  Week of: {week_of}")

    # Send notification (placeholder for SendGrid integration)
    if SENDGRID_API_KEY:
        print(f"  📧 Email notification ready (SendGrid configured)")
    else:
        print(f"  📧 Email notification skipped (SENDGRID_API_KEY not set)")


if __name__ == "__main__":
    main()
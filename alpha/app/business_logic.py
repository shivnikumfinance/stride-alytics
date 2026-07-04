"""
Alpha Option Trading System — Business Logic Module
Implements scoring, band classification, daily filters, weekly watchlist,
volatility logic, trend logic, and strategy tagging.

This module is the core “brains” of the Alpha system.
"""

import pandas as pd
from datetime import datetime, timedelta


# ─────────────────────────────────────────────
# 1. Option Score Logic
# ─────────────────────────────────────────────


def compute_option_score(row: pd.Series) -> int:
    """Compute the 0–9 Option Score for a single ticker row."""

    score = 0

    # Liquidity
    if row.get("option_volume", 0) > 2000:
        score += 1
    if row.get("max_oi_near_exp", 0) > 500:
        score += 1
    if row.get("bid_ask_spread_pct", 1) < 0.08:
        score += 1

    # Volatility
    if row.get("iv_30d", 0) > 0.25:
        score += 1
    if row.get("iv_rank_1y", 0) >= 40:
        score += 1

    # Risk
    price = row.get("price", 0)
    atr = row.get("atr", 0)
    if price > 0 and (atr / price) < 0.04:
        score += 1

    earnings_date = row.get("next_earnings_date")
    if isinstance(earnings_date, str):
        earnings_date = datetime.fromisoformat(earnings_date)

    if earnings_date and earnings_date > datetime.now() + timedelta(days=14):
        score += 1

    if row.get("short_interest_pct", 100) < 15:
        score += 1

    # Fundamentals
    if row.get("quality_score", 0) >= 3:
        score += 1

    return score


# ─────────────────────────────────────────────
# 2. Band Classification Logic
# ─────────────────────────────────────────────


def classify_band(score: int) -> str:
    """Assign Band A–E based on Option Score."""
    if score >= 8:
        return "A"
    if score >= 6:
        return "B"
    if score >= 4:
        return "C"
    if score >= 2:
        return "D"
    return "E"


# ─────────────────────────────────────────────
# 3. Daily Filter Logic
# ─────────────────────────────────────────────


def passes_daily_filters(row: pd.Series) -> bool:
    """Return True if ticker passes all daily filters."""
    # Check required daily filters
    option_volume = row.get("option_volume", 0)
    max_oi = row.get("max_oi_near_exp", 0)
    spread_pct = row.get("bid_ask_spread_pct", 100)
    earnings_date = row.get("next_earnings_date")
    short_interest = row.get("short_interest_pct", 100)

    # Apply daily filter criteria
    if option_volume < 2000:
        return False
    if max_oi < 500:
        return False
    if spread_pct > 0.08:
        return False
    if short_interest >= 15:
        return False

    # Check earnings date (must be more than 14 days away)
    if earnings_date:
        if isinstance(earnings_date, str):
            earnings_date = datetime.fromisoformat(earnings_date)
        if isinstance(earnings_date, datetime):
            if earnings_date <= datetime.now() + timedelta(days=14):
                return False

    return True

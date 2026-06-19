"""Screener service — filter options chains by user-supplied criteria.

In Phase 1 we work against in-memory fixtures so the endpoint contract
is testable end-to-end without a market-data vendor. A future iteration
will swap ``_load_chain()`` for a Supabase-backed query against the
``options`` table populated by ``scheduler/scripts/fetch_market_data.py``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, timedelta

from app.services.greeks import calculate_greeks
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

log = get_logger(__name__)


@dataclass
class ScreenerFilters:
    symbol: str
    min_strike: float | None = None
    max_strike: float | None = None
    expiry_days_min: int = 0
    expiry_days_max: int = 60
    option_type: str | None = None  # 'call' | 'put' | None (=both)
    min_volume: int = 0
    min_open_interest: int = 0
    max_iv: float | None = None
    min_iv: float | None = None
    limit: int = 50


def _load_chain(symbol: str, spot: float) -> list[dict]:
    """Synthetic option chain — replaced by DB lookup in Phase 2."""
    rng = random.Random(hash(symbol) & 0xFFFFFFFF)
    chain: list[dict] = []
    base_date = date.today()
    for d in (7, 14, 30, 60):
        expiry = base_date + timedelta(days=d)
        for strike in (spot * m for m in (0.9, 0.95, 1.0, 1.05, 1.1)):
            for opt_type in ("call", "put"):
                iv = round(rng.uniform(0.15, 0.65), 4)
                t = d / 365.0
                greeks = calculate_greeks(
                    spot=spot,
                    strike=strike,
                    time_to_expiry=t,
                    volatility=iv,
                    option_type=opt_type,
                )
                mid = greeks.price_call if opt_type == "call" else greeks.price_put
                chain.append(
                    {
                        "symbol": symbol,
                        "strike": round(strike, 2),
                        "expiry": expiry.isoformat(),
                        "option_type": opt_type,
                        "bid": round(mid * 0.99, 4),
                        "ask": round(mid * 1.01, 4),
                        "last_price": round(mid, 4),
                        "implied_vol": iv,
                        "delta": greeks.delta,
                        "gamma": greeks.gamma,
                        "theta": greeks.theta,
                        "vega": greeks.vega,
                        "open_interest": rng.randint(10, 5000),
                        "volume": rng.randint(0, 20_000),
                    }
                )
    return chain


def _get_spot(symbol: str) -> float:
    """Stub spot lookup. In Phase 2, read from the ``options`` table or
    a price cache populated by the scheduler."""
    table = {"AAPL": 195.0, "MSFT": 415.0, "TSLA": 245.0, "SPY": 555.0}
    if symbol in table:
        return table[symbol]
    # Deterministic pseudo-spot for arbitrary tickers
    return round(50 + (hash(symbol) % 400), 2)


def run_screener(filters: ScreenerFilters) -> dict:
    """Execute the screener and return a structured response payload."""
    symbol = normalize_symbol(filters.symbol)
    spot = _get_spot(symbol)
    chain = _load_chain(symbol, spot)

    today = date.today()
    results: list[dict] = []
    for row in chain:
        expiry = date.fromisoformat(row["expiry"])
        dte = (expiry - today).days
        if not (filters.expiry_days_min <= dte <= filters.expiry_days_max):
            continue
        if filters.option_type and row["option_type"] != filters.option_type:
            continue
        if filters.min_strike is not None and row["strike"] < filters.min_strike:
            continue
        if filters.max_strike is not None and row["strike"] > filters.max_strike:
            continue
        if row["volume"] < filters.min_volume:
            continue
        if row["open_interest"] < filters.min_open_interest:
            continue
        if filters.min_iv is not None and row["implied_vol"] < filters.min_iv:
            continue
        if filters.max_iv is not None and row["implied_vol"] > filters.max_iv:
            continue
        results.append(row)

    results.sort(key=lambda r: (-r["volume"], r["strike"]))
    truncated = results[: filters.limit]

    log.info(
        "screener.run",
        symbol=symbol,
        spot=spot,
        matched=len(results),
        returned=len(truncated),
    )

    return {
        "symbol": symbol,
        "spot": spot,
        "count": len(truncated),
        "results": truncated,
    }

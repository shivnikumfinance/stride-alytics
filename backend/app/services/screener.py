"""Screener service — filter options chains by user-supplied criteria.

Data comes from yfinance. When yfinance is unavailable the screener falls back
to a *synthetic* chain so the UI keeps working in dev; that data is random and
must never be mistaken for (or stored as) market data, so every result carries
a ``source`` of ``"live"`` or ``"synthetic"``.
"""

from __future__ import annotations

import math
import random
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import httpx
import yfinance as yf

from app.services.greeks import calculate_greeks
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

log = get_logger(__name__)


# --- Tracked symbols for scheduler integration ---
TRACKED_SYMBOLS = ["SPY", "QQQ", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "AMD"]


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


def _stable_seed(text: str) -> int:
    """Process-independent seed (``hash()`` of a str is randomized per run)."""
    return zlib.crc32(text.encode())


def _get_spot_from_yfinance(symbol: str) -> float | None:
    """Fetch the latest spot price via yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
        # Fallback to fast_info
        info = ticker.fast_info
        if hasattr(info, "last_price"):
            return float(info.last_price)
        return None
    except Exception as exc:
        log.warning("screener.yfinance_spot_failed", symbol=symbol, error=str(exc))
        return None


def _chain_row_greeks(
    spot: float, strike: float, dte: int, iv: float, option_type: str
) -> dict[str, float]:
    """Black-Scholes Greeks (yfinance chains do not include them)."""
    try:
        g = calculate_greeks(
            spot=spot,
            strike=strike,
            time_to_expiry=max(dte, 0.5) / 365.0,
            volatility=iv,
            option_type=option_type,
        )
    except ValueError:
        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
    return {"delta": g.delta, "gamma": g.gamma, "theta": g.theta, "vega": g.vega}


def _load_chain_from_yfinance(symbol: str, spot: float) -> list[dict[str, Any]] | None:
    """Fetch the option chain from yfinance.

    Returns ``None`` if nothing usable could be fetched (callers decide
    whether to fall back). ``spot`` is used to compute the Greeks.
    """
    try:
        ticker = yf.Ticker(symbol)
        options: list[dict[str, Any]] = []
        try:
            expirations = ticker.options
        except Exception:
            expirations = None

        if not expirations:
            log.warning("screener.no_expirations", symbol=symbol)
            return None

        today = date.today()
        # Limit to the next 3 expiration cycles for performance
        for expiry_str in expirations[:3]:
            try:
                opt_chain = ticker.option_chain(expiry_str)
                dte = (date.fromisoformat(expiry_str) - today).days

                for opt_type, chain_data in [("call", opt_chain.calls), ("put", opt_chain.puts)]:
                    for _, row in chain_data.iterrows():
                        iv = float(row.get("impliedVolatility", 0.3))
                        if math.isnan(iv) or iv <= 0:
                            iv = 0.3
                        strike = float(row.get("strike", 0))
                        greeks = _chain_row_greeks(spot, strike, dte, iv, opt_type)
                        options.append(
                            {
                                "symbol": symbol,
                                "strike": strike,
                                "expiry": expiry_str,
                                "option_type": opt_type,
                                "bid": float(row.get("bid", 0) or 0),
                                "ask": float(row.get("ask", 0) or 0),
                                "last_price": float(row.get("lastPrice", 0) or 0),
                                "implied_vol": round(iv, 4),
                                **greeks,
                                "open_interest": int(row.get("openInterest", 0) or 0),
                                "volume": int(row.get("volume", 0) or 0),
                            }
                        )
            except Exception as exc:
                log.warning(
                    "screener.option_chain_failed", symbol=symbol, expiry=expiry_str, error=str(exc)
                )
                continue

        return options or None

    except Exception as exc:
        log.warning("screener.yfinance_failed", symbol=symbol, error=str(exc))
        return None


def _load_chain_synthetic(symbol: str, spot: float) -> list[dict[str, Any]]:
    """Synthetic option chain — random placeholder data, NOT market data."""
    rng = random.Random(_stable_seed(symbol))
    chain: list[dict[str, Any]] = []
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


def _get_fallback_spot(symbol: str) -> float:
    """Placeholder spot prices when yfinance is unavailable (NOT live prices)."""
    table = {
        "AAPL": 195.0,
        "MSFT": 415.0,
        "TSLA": 245.0,
        "SPY": 555.0,
        "QQQ": 480.0,
        "AMZN": 185.0,
        "GOOGL": 175.0,
        "META": 510.0,
        "NVDA": 130.0,
        "AMD": 160.0,
    }
    if symbol in table:
        return table[symbol]
    return round(50 + (_stable_seed(symbol) % 400), 2)


async def fetch_and_cache_supabase(symbol: str, supabase_url: str, supabase_key: str) -> bool:
    """Fetch the live option chain via yfinance and upsert into Supabase ``options``.

    Called by the scheduler (fetch_market_data.py). Returns True on success.
    Synthetic data is never cached: if live data is unavailable this returns
    False without writing anything.
    """
    spot = _get_spot_from_yfinance(symbol)
    if spot is None or spot <= 0:
        log.warning("screener.cache_skipped_no_live_spot", symbol=symbol)
        return False

    chain = _load_chain_from_yfinance(symbol, spot)
    if not chain:
        log.warning("screener.cache_skipped_no_live_chain", symbol=symbol)
        return False

    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

    # Upsert in batches of 100 to avoid payload size limits
    batch_size = 100
    for i in range(0, len(chain), batch_size):
        batch = chain[i : i + batch_size]
        for row in batch:
            row["updated_at"] = date.today().isoformat()
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{supabase_url}/rest/v1/options",
                    headers=headers,
                    json=batch,
                )
                if resp.status_code >= 400:
                    log.warning(
                        "screener.supabase_upsert_failed",
                        symbol=symbol,
                        status=resp.status_code,
                        body=resp.text[:200],
                    )
        except Exception as exc:
            log.error("screener.supabase_upsert_error", symbol=symbol, error=str(exc))
            return False

    log.info("screener.cached_to_supabase", symbol=symbol, count=len(chain))
    return True


def _get_spot(symbol: str) -> tuple[float, bool]:
    """Return ``(spot, is_live)``; falls back to a static placeholder table."""
    symbol = normalize_symbol(symbol)
    spot = _get_spot_from_yfinance(symbol)
    if spot and spot > 0:
        log.info("screener.spot_from_yfinance", symbol=symbol, spot=spot)
        return spot, True
    log.warning("screener.spot_fallback", symbol=symbol)
    return _get_fallback_spot(symbol), False


def _load_chain(symbol: str, spot: float) -> tuple[list[dict[str, Any]], bool]:
    """Return ``(chain, is_live)``; falls back to a synthetic chain."""
    symbol = normalize_symbol(symbol)
    chain = _load_chain_from_yfinance(symbol, spot)
    if chain:
        log.info("screener.using_yfinance", symbol=symbol, contracts=len(chain))
        return chain, True
    log.warning("screener.using_synthetic_chain", symbol=symbol)
    return _load_chain_synthetic(symbol, spot), False


ChainProvider = Callable[[str], tuple[float, list[dict[str, Any]], str]]


def load_chain(symbol: str) -> tuple[float, list[dict[str, Any]], str]:
    """(spot, chain rows, source). ``source`` is ``live`` only when both came from yfinance."""
    sym = normalize_symbol(symbol)
    spot, spot_live = _get_spot(sym)
    chain, chain_live = _load_chain(sym, spot)
    return spot, chain, "live" if (spot_live and chain_live) else "synthetic"


def get_chain_provider() -> ChainProvider:
    """FastAPI dependency; tests override it with a fake."""
    return load_chain


def run_screener(filters: ScreenerFilters) -> dict[str, Any]:
    """Execute the screener and return a structured response payload.

    ``source`` is ``"live"`` only when both the spot price and the chain came
    from yfinance; otherwise ``"synthetic"``.
    """
    symbol = normalize_symbol(filters.symbol)
    spot, spot_live = _get_spot(symbol)
    chain, chain_live = _load_chain(symbol, spot)
    source = "live" if (spot_live and chain_live) else "synthetic"

    today = date.today()
    results: list[dict[str, Any]] = []
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
        source=source,
        matched=len(results),
        returned=len(truncated),
    )

    return {
        "symbol": symbol,
        "spot": spot,
        "count": len(truncated),
        "results": truncated,
        "source": source,
    }

"""Live prices and Greeks for open positions (yfinance), with a short cache.

Best-effort: whatever cannot be fetched stays ``None`` and ``available`` is False, so the alert
rules skip the price-based checks instead of guessing. Blocking (network): callers use a thread.
Injected as a dependency so tests can substitute a fake.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from datetime import date

from app.domain.alerts import CONTRACT_MULTIPLIER, MarketInput
from app.services.greeks import calculate_greeks
from app.utils.logger import get_logger

log = get_logger(__name__)

CACHE_TTL_SECONDS = 60
PositionDataProvider = Callable[..., MarketInput]

_lock = threading.Lock()
_cache: dict[tuple, tuple[float, MarketInput]] = {}


def clear_cache() -> None:
    with _lock:
        _cache.clear()


def _spot(ticker: object) -> float | None:
    try:
        price = ticker.fast_info["last_price"]  # type: ignore[attr-defined]
        if price and price > 0:
            return float(price)
    except Exception:  # noqa: BLE001
        pass
    try:
        hist = ticker.history(period="1d")  # type: ignore[attr-defined]
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except Exception:  # noqa: BLE001
        pass
    return None


def _option_quote(ticker: object, expiry: date, strike: float, trade_type: str):
    """(mark, implied vol) for one contract, or (None, None)."""
    try:
        chain = ticker.option_chain(expiry.isoformat())  # type: ignore[attr-defined]
        frame = chain.calls if trade_type == "call" else chain.puts
        row = frame[(frame["strike"] - strike).abs() < 1e-6]
        if row.empty:
            return None, None
        bid, ask = float(row.iloc[0]["bid"]), float(row.iloc[0]["ask"])
        last = float(row.iloc[0]["lastPrice"])
        iv = float(row.iloc[0]["impliedVolatility"])
        mark = (bid + ask) / 2 if bid > 0 and ask > 0 else (last if last > 0 else None)
        return mark, (iv if iv == iv and iv > 0 else None)
    except Exception as exc:  # noqa: BLE001
        log.warning("position_data.chain_failed", error=str(exc))
        return None, None


def fetch_position_market(
    symbol: str,
    *,
    trade_type: str,
    strike: float | None = None,
    expiry: date | None = None,
) -> MarketInput:
    key = (symbol, trade_type, strike, expiry)
    now = time.monotonic()
    with _lock:
        hit = _cache.get(key)
        if hit and now - hit[0] < CACHE_TTL_SECONDS:
            return hit[1]

    result = MarketInput(available=False)
    try:
        import yfinance as yf

        ticker = yf.Ticker(symbol)
        spot = _spot(ticker)
        if trade_type == "stock":
            result = MarketInput(available=spot is not None, spot=spot, mark=spot)
        elif strike and expiry:
            mark, iv = _option_quote(ticker, expiry, strike, trade_type)
            delta = theta = None
            if spot and iv:
                try:
                    days = max((expiry - date.today()).days, 0.5)
                    g = calculate_greeks(
                        spot=spot,
                        strike=strike,
                        time_to_expiry=days / 365.0,
                        volatility=iv,
                        option_type=trade_type,
                    )
                    delta, theta = g.delta, round(g.theta * CONTRACT_MULTIPLIER, 2)
                except ValueError:
                    pass
            result = MarketInput(
                available=spot is not None or mark is not None,
                spot=spot,
                mark=mark,
                delta=delta,
                theta=theta,
                iv=iv,
            )
    except Exception as exc:  # noqa: BLE001
        log.warning("position_data.failed", symbol=symbol, error=str(exc))

    if result.available:  # failures are not cached, so the next request retries
        with _lock:
            _cache[key] = (now, result)
    return result


def get_position_data_provider() -> PositionDataProvider:
    """FastAPI dependency; tests override it with a fake."""
    return fetch_position_market

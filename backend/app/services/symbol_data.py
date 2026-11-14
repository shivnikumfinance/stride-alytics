"""Fetch what the gate needs to know about a candidate trade (yfinance).

Every lookup is best-effort: anything that cannot be fetched stays ``None`` so the gate blocks
with a "data unavailable" reason instead of guessing. This module is blocking (network); callers
run it in a thread. It is injected as a dependency so tests can substitute a fake.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime

from app.domain.gate import SymbolData
from app.utils.logger import get_logger

log = get_logger(__name__)

SymbolDataProvider = Callable[..., SymbolData]


def _first_future_date(calendar: object, today: date) -> date | None:
    """Pick the next earnings date from yfinance's ``calendar`` (dict-like)."""
    try:
        raw = calendar.get("Earnings Date") if hasattr(calendar, "get") else None  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        return None
    if raw is None:
        return None
    items = raw if isinstance(raw, (list, tuple)) else [raw]
    dates: list[date] = []
    for item in items:
        if isinstance(item, datetime):
            dates.append(item.date())
        elif isinstance(item, date):
            dates.append(item)
    future = sorted(d for d in dates if d >= today)
    return future[0] if future else (sorted(dates)[-1] if dates else None)


def _contract_liquidity(
    ticker: object, expiry: date, strike: float, option_type: str
) -> tuple[float | None, int | None]:
    """(spread % of mid, open interest) for one contract, or (None, None)."""
    try:
        chain = ticker.option_chain(expiry.isoformat())  # type: ignore[attr-defined]
        frame = chain.calls if option_type == "call" else chain.puts
        row = frame[(frame["strike"] - strike).abs() < 1e-6]
        if row.empty:
            return None, None
        bid, ask = float(row.iloc[0]["bid"]), float(row.iloc[0]["ask"])
        oi_raw = row.iloc[0]["openInterest"]
        oi = None if oi_raw != oi_raw else int(oi_raw)  # NaN -> None
        if bid <= 0 or ask <= 0 or ask < bid:
            return None, oi
        mid = (bid + ask) / 2
        return round((ask - bid) / mid * 100, 2), oi
    except Exception as exc:  # noqa: BLE001
        log.warning("symbol_data.chain_failed", error=str(exc))
        return None, None


def fetch_symbol_data(
    symbol: str,
    *,
    trade_type: str,
    strike: float | None = None,
    expiry: date | None = None,
    option_type: str | None = None,
) -> SymbolData:
    """Market cap, quote type, next earnings and (for options) spread and open interest."""
    try:
        import yfinance as yf
    except Exception:  # noqa: BLE001
        return SymbolData(symbol=symbol, fetched=False)

    today = date.today()
    data = SymbolData(symbol=symbol, fetched=False)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        if info:
            data.fetched = True
            data.quote_type = info.get("quoteType")
            cap = info.get("marketCap")
            data.market_cap = float(cap) if cap else None
        try:
            data.next_earnings = _first_future_date(ticker.calendar, today)
        except Exception:  # noqa: BLE001
            data.next_earnings = None
        if trade_type in ("call", "put") and strike and expiry:
            data.spread_pct, data.open_interest = _contract_liquidity(
                ticker, expiry, strike, option_type or trade_type
            )
    except Exception as exc:  # noqa: BLE001
        log.warning("symbol_data.failed", symbol=symbol, error=str(exc))
    return data


def get_symbol_data_provider() -> SymbolDataProvider:
    """FastAPI dependency; tests override it with a fake."""
    return fetch_symbol_data

"""Sector lookup for exposure reporting (yfinance), cached for the life of the process.

Best-effort: an unknown sector is ``None`` and shows up as "Unknown", never a guess. Blocking
(network); callers use a thread. Injected as a dependency so tests can substitute a fake.
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from app.utils.logger import get_logger

log = get_logger(__name__)

SectorProvider = Callable[[str], str | None]

_lock = threading.Lock()
_cache: dict[str, str | None] = {}


def fetch_sector(symbol: str) -> str | None:
    with _lock:
        if symbol in _cache:
            return _cache[symbol]
    sector: str | None = None
    try:
        import yfinance as yf

        info = yf.Ticker(symbol).info or {}
        raw = info.get("sector")
        if not raw and info.get("quoteType") in ("ETF", "INDEX", "MUTUALFUND"):
            raw = "ETF / Index"
        sector = raw or None
    except Exception as exc:  # noqa: BLE001
        log.warning("sector_data.failed", symbol=symbol, error=str(exc))
        return None  # failures are not cached
    with _lock:
        _cache[symbol] = sector
    return sector


def get_sector_provider() -> SectorProvider:
    """FastAPI dependency; tests override it with a fake."""
    return fetch_sector

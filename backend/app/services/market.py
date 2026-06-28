"""Market data service — owns all external data fetching + fallbacks.

The endpoint layer (``app.api.v1.endpoints.market``) must remain a thin
adapter that delegates here. The reasoning:

* Centralizes URL, headers, timeouts, and retries.
* Makes the data source swappable without touching HTTP plumbing.
* Allows tests to monkeypatch this module.
* Keeps schemas separate from business logic.
"""

from __future__ import annotations

from typing import Final

import httpx

from app.api.v1.schemas.market import TickerData
from app.utils.logger import get_logger

router = None  # placeholder to keep tooling quiet; not used here

YAHOO_API_URL: Final[str] = "https://query1.finance.yahoo.com/v7/finance/quote"

DEFAULT_TICKERS: Final[tuple[str, ...]] = ("SPY", "QQQ", "DIA", "VIX")

YAHOO_FIELDS: Final[str] = (
    "symbol,regularMarketPrice,regularMarketChange,regularMarketChangePercent"
)

YAHOO_HEADERS: Final[dict[str, str]] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ),
}

# Graceful fallback so the dashboard never goes empty in dev / when Yahoo 429s.
MOCK_TICKERS: Final[dict[str, TickerData]] = {
    "SPY": TickerData(symbol="SPY", price="548.32", change="-1.23", changePercent="-0.22"),
    "QQQ": TickerData(symbol="QQQ", price="478.92", change="2.15", changePercent="+0.45"),
    "DIA": TickerData(symbol="DIA", price="395.61", change="0.89", changePercent="+0.22"),
    "VIX": TickerData(symbol="VIX", price="15.42", change="-0.58", changePercent="-3.63"),
}

REQUEST_TIMEOUT_SECONDS: Final[float] = 10.0

log = get_logger(__name__)


def _to_ticker(quote: dict) -> TickerData:
    """Convert one Yahoo quote row into a ``TickerData``."""
    return TickerData(
        symbol=str(quote.get("symbol") or ""),
        price=str(round(float(quote.get("regularMarketPrice") or 0), 2)),
        change=str(round(float(quote.get("regularMarketChange") or 0), 2)),
        changePercent=str(round(float(quote.get("regularMarketChangePercent") or 0), 2)),
    )


async def fetch_tickers(symbols: tuple[str, ...] = DEFAULT_TICKERS) -> dict[str, TickerData]:
    """Fetch ticker data for ``symbols``.

    Always returns a non‑empty ``{ SYM: TickerData }`` map — falls back to
    :data:`MOCK_TICKERS` on any network/HTTP/parse failure so the frontend
    never receives an empty payload during a Yahoo outage.
    """
    try:
        params = {"symbols": ",".join(symbols), "fields": YAHOO_FIELDS}
        log.info("market.tickers_fetching", symbols=",".join(symbols))

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:
            response = await client.get(YAHOO_API_URL, params=params, headers=YAHOO_HEADERS)
            response.raise_for_status()

            data = response.json()
            quotes = (data.get("quoteResponse") or {}).get("result") or []

            if not quotes:
                log.warning("market.tickers_no_results")
                return dict(MOCK_TICKERS)

            result: dict[str, TickerData] = {}
            for quote in quotes:
                if not quote or not quote.get("symbol"):
                    continue
                ticker = _to_ticker(quote)
                if ticker.symbol:
                    result[ticker.symbol] = ticker

            if not result:
                return dict(MOCK_TICKERS)

            log.info(
                "market.tickers_served",
                ticker_count=len(result),
                symbols=list(result.keys()),
            )
            return result

    except httpx.TimeoutException as exc:
        log.warning("market.tickers_timeout", error=str(exc))
        return dict(MOCK_TICKERS)
    except httpx.HTTPError as exc:
        log.error(
            "market.tickers_http_error",
            error=str(exc),
            status_code=getattr(getattr(exc, "response", None), "status_code", "unknown"),
        )
        return dict(MOCK_TICKERS)
    except Exception as exc:  # last‑resort fallback so the UI never breaks
        log.error(
            "market.tickers_failed",
            error=str(exc),
            error_type=type(exc).__name__,
        )
        return dict(MOCK_TICKERS)

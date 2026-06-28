"""Market data endpoints — GET /api/v1/market/tickers."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException

from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)

YAHOO_API_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
TICKERS = ["SPY", "QQQ", "DIA", "VIX"]

# Fallback mock data for testing
MOCK_TICKERS = {
    "SPY": {"symbol": "SPY", "price": "548.32", "change": "-1.23", "changePercent": "-0.22"},
    "QQQ": {"symbol": "QQQ", "price": "478.92", "change": "2.15", "changePercent": "+0.45"},
    "DIA": {"symbol": "DIA", "price": "395.61", "change": "0.89", "changePercent": "+0.22"},
    "VIX": {"symbol": "VIX", "price": "15.42", "change": "-0.58", "changePercent": "-3.63"},
}


class TickerData:
    """Simple ticker data model."""

    def __init__(self, symbol: str, price: float, change: float, changePercent: float):
        self.symbol = symbol
        self.price = round(price, 2)
        self.change = round(change, 2)
        self.changePercent = round(changePercent, 2)

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "price": str(self.price),
            "change": str(self.change),
            "changePercent": str(self.changePercent),
        }


@router.get("/tickers")
async def get_market_tickers() -> dict:
    """
    Fetch real-time market data for major indexes (SPY, QQQ, DIA, VIX).

    Returns a dict with symbol keys and ticker data values.
    Provides a CORS-compliant proxy to Yahoo Finance API.
    Falls back to mock data if API is unavailable.
    """
    try:
        params = {
            "symbols": ",".join(TICKERS),
            "fields": "symbol,regularMarketPrice,regularMarketChange,regularMarketChangePercent",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        log.info("market.tickers_fetching", symbols=",".join(TICKERS))

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(YAHOO_API_URL, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            quotes = data.get("quoteResponse", {}).get("result", [])

            if not quotes:
                log.warning("market.tickers_no_results")
                # Fallback to mock data
                return {"success": True, "data": MOCK_TICKERS}

            result = {}
            for quote in quotes:
                if quote and quote.get("symbol"):
                    ticker = TickerData(
                        symbol=quote.get("symbol", ""),
                        price=quote.get("regularMarketPrice", 0),
                        change=quote.get("regularMarketChange", 0),
                        changePercent=quote.get("regularMarketChangePercent", 0),
                    )
                    result[ticker.symbol] = ticker.to_dict()

            log.info("market.tickers_served", ticker_count=len(result), symbols=list(result.keys()))
            return {"success": True, "data": result}

    except httpx.TimeoutException as e:
        log.warning("market.tickers_timeout", error=str(e))
        # Return mock data on timeout
        return {"success": True, "data": MOCK_TICKERS}
    except httpx.HTTPError as e:
        log.error("market.tickers_http_error", error=str(e), status_code=getattr(e.response, "status_code", "unknown"))
        # Return mock data on HTTP errors
        return {"success": True, "data": MOCK_TICKERS}
    except Exception as e:
        log.error("market.tickers_failed", error=str(e), error_type=type(e).__name__)
        # Return mock data as graceful fallback
        return {"success": True, "data": MOCK_TICKERS}

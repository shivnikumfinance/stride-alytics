"""Market endpoints — GET /api/v1/market/tickers.

Thin adapter only: HTTP → service → schema. Business logic (URL, headers,
fallback data, parsing) lives in :mod:`app.services.market`.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.schemas.market import TickerEnvelope
from app.services.market import fetch_tickers
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.get("/tickers", response_model=TickerEnvelope)
async def get_market_tickers() -> TickerEnvelope:
    """Return a CORS‑compliant proxy of Yahoo Finance for major index tickers.

    On any upstream failure the service falls back to a static snapshot so
    the frontend dashboard never sees an empty payload.
    """
    data = await fetch_tickers()
    return TickerEnvelope(success=True, data=data)

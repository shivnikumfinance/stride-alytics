"""Market endpoints — GET /api/v1/market/tickers.

Thin adapter only: HTTP → service → schema. Business logic (URL, headers,
fallback data, parsing) lives in :mod:`app.services.market`.
"""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, Query

from app.api.v1.schemas.market import TickerEnvelope
from app.services.market import DEFAULT_TICKERS, fetch_tickers_with_source
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)

MAX_SYMBOLS = 25
_SYMBOL_RE = re.compile(r"^[A-Z0-9.^=-]{1,12}$")


@router.get("/tickers", response_model=TickerEnvelope)
async def get_market_tickers(
    symbols: str | None = Query(
        default=None,
        description=f"Comma-separated symbols (max {MAX_SYMBOLS}); defaults to the index tickers",
    ),
) -> TickerEnvelope:
    """Return a CORS‑compliant proxy of Yahoo Finance quotes.

    On any upstream failure the service falls back to a static snapshot so
    the frontend dashboard never sees an empty payload; ``source`` is then
    ``"fallback"``.
    """
    if symbols is None:
        wanted = DEFAULT_TICKERS
    else:
        parts = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not parts or len(parts) > MAX_SYMBOLS or any(not _SYMBOL_RE.match(s) for s in parts):
            raise HTTPException(
                status_code=422,
                detail=f"symbols must be 1-{MAX_SYMBOLS} comma-separated tickers",
            )
        wanted = tuple(dict.fromkeys(parts))
    data, source = await fetch_tickers_with_source(wanted)
    return TickerEnvelope(success=True, data=data, source=source)

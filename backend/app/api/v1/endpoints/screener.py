"""Screener endpoints — POST /api/v1/screener/run and GET /api/v1/screener/limits."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.screener import ScreenerQuery, ScreenerResponse
from app.services.screener import ScreenerFilters, run_screener
from app.utils.constants import SCREENER_MAX_RESULTS
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/run", response_model=ScreenerResponse)
async def run(
    payload: ScreenerQuery,
    current_user: CurrentUser = Depends(get_current_user),
) -> ScreenerResponse:
    """Run the options screener with the supplied filters.

    Results are capped at ``SCREENER_MAX_RESULTS``.
    """
    if payload.limit > SCREENER_MAX_RESULTS:
        payload.limit = SCREENER_MAX_RESULTS

    filters = ScreenerFilters(**payload.model_dump())
    result = run_screener(filters)

    log.info(
        "screener.run",
        user_id=current_user.user_id,
        symbol=payload.symbol,
        returned=result["count"],
    )

    return ScreenerResponse(
        symbol=result["symbol"],
        spot=result["spot"],
        count=result["count"],
        results=result["results"],
    )


@router.get("/limits")
async def limits(current_user: CurrentUser = Depends(get_current_user)) -> dict[str, Any]:
    """Return the screener limits."""
    return {
        "success": True,
        "data": {
            "max_results_per_call": SCREENER_MAX_RESULTS,
        },
    }

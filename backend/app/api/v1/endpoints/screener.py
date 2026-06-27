"""Screener endpoints — POST /api/v1/screener/run and GET /api/v1/screener/limits."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.screener import ScreenerQuery, ScreenerResponse
from app.services.screener import ScreenerFilters, run_screener
from app.utils.constants import (
    FREE_TIER_SCREENER_LIMIT,
    PRO_TIER_SCREENER_LIMIT,
)
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/run", response_model=ScreenerResponse)
async def run(
    payload: ScreenerQuery,
    current_user: CurrentUser = Depends(get_current_user),
) -> ScreenerResponse:
    """Run the options screener with the supplied filters.

    Free-tier users are capped at ``FREE_TIER_SCREENER_LIMIT`` results;
    pro users at ``PRO_TIER_SCREENER_LIMIT``.
    """
    max_limit = (
        PRO_TIER_SCREENER_LIMIT
        if current_user.plan == "pro"
        else FREE_TIER_SCREENER_LIMIT
    )
    if payload.limit > max_limit:
        if current_user.plan == "free":
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=(
                    f"Free tier limit is {FREE_TIER_SCREENER_LIMIT} results. "
                    "Upgrade to Pro for unlimited screening."
                ),
            )
        payload.limit = max_limit

    filters = ScreenerFilters(**payload.model_dump())
    result = run_screener(filters)

    log.info(
        "screener.run",
        user_id=current_user.user_id,
        plan=current_user.plan,
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
async def limits(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    """Return the caller's current screener limits."""
    max_limit = (
        PRO_TIER_SCREENER_LIMIT
        if current_user.plan == "pro"
        else FREE_TIER_SCREENER_LIMIT
    )
    return {
        "success": True,
        "data": {
            "plan": current_user.plan,
            "max_results_per_call": max_limit,
        },
    }

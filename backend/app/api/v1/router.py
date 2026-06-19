"""Main API v1 router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, greeks, portfolio, regime, screener, trades

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(screener.router, prefix="/screener", tags=["screener"])
router.include_router(greeks.router, prefix="/greeks", tags=["greeks"])
router.include_router(regime.router, prefix="/regime", tags=["regime"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
router.include_router(trades.router, prefix="/trades", tags=["trades"])


@router.get("/health", tags=["health"])
async def health() -> dict:
    """Liveness probe for the API surface."""
    return {"success": True, "data": {"status": "ok"}}

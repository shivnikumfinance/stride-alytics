"""Main API v1 router — aggregates all endpoint routers.

Single source of truth for the public URL surface. To add a new resource:
1. Create ``app/api/v1/endpoints/<name>.py`` exposing ``router``.
2. Create ``app/api/v1/schemas/<name>.py`` with Pydantic models.
3. Create ``app/services/<name>.py`` with business logic (no HTTP).
4. Register the endpoint router below with the correct ``prefix`` and ``tags``.
5. Re‑export the schemas and services from their respective ``__init__.py``.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, greeks, market, portfolio, regime, screener, trades

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(market.router, prefix="/market", tags=["market"])
router.include_router(screener.router, prefix="/screener", tags=["screener"])
router.include_router(greeks.router, prefix="/greeks", tags=["greeks"])
router.include_router(regime.router, prefix="/regime", tags=["regime"])
router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
router.include_router(trades.router, prefix="/trades", tags=["trades"])


@router.get("/health", tags=["health"])
async def health() -> dict:
    """Liveness probe for the API surface."""
    return {"success": True, "data": {"status": "ok"}}

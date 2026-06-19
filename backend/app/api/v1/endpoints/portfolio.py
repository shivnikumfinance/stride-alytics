"""Portfolio endpoints — list/create portfolios + summary."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.portfolio import PortfolioCreate, PortfolioSummary
from app.services.portfolio import store as portfolio_store, summary as portfolio_summary_fn
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


def _looks_like_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _user_uuid(user_id: str) -> UUID | None:
    return UUID(user_id) if _looks_like_uuid(user_id) else None


@router.get("")
async def list_portfolios(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """List all portfolios owned by the authenticated user."""
    user_uuid = _user_uuid(current_user.user_id)
    if user_uuid is None:
        return {"success": True, "data": []}
    items = portfolio_store.list_portfolios(user_uuid)
    return {
        "success": True,
        "data": [
            {"id": str(p.id), "name": p.name, "description": p.description}
            for p in items
        ],
    }


@router.post("", response_model=PortfolioSummary, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> PortfolioSummary:
    """Create a new portfolio for the authenticated user."""
    user_uuid = _user_uuid(current_user.user_id) or UUID(int=0)
    try:
        portfolio = portfolio_store.create_portfolio(
            user_id=user_uuid,
            name=payload.name,
            description=payload.description,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc

    log.info("portfolio.created", user_id=current_user.user_id, name=payload.name)
    return PortfolioSummary(**portfolio_summary_fn(portfolio))


@router.get("/{portfolio_id}", response_model=PortfolioSummary)
async def portfolio_summary_endpoint(
    portfolio_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> PortfolioSummary:
    """Return aggregate stats for a single portfolio."""
    user_uuid = _user_uuid(current_user.user_id)
    if user_uuid is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    try:
        portfolio = portfolio_store.get_portfolio(user_uuid, portfolio_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    return PortfolioSummary(**portfolio_summary_fn(portfolio))

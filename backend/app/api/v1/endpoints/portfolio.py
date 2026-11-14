"""Portfolio endpoints — list/create/update/delete portfolios + summary."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import Ctx, get_ctx
from app.api.v1.schemas.portfolio import PortfolioCreate, PortfolioSummary, PortfolioUpdate
from app.services.portfolio import summary as portfolio_summary_fn
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.get("")
async def list_portfolios(ctx: Ctx = Depends(get_ctx)) -> dict[str, Any]:
    """List all portfolios owned by the authenticated user."""
    items = await ctx.repo.list_portfolios(ctx.user_id)
    return {
        "success": True,
        "data": [{"id": str(p.id), "name": p.name, "description": p.description} for p in items],
    }


@router.post("", response_model=PortfolioSummary, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate, ctx: Ctx = Depends(get_ctx)
) -> PortfolioSummary:
    """Create a new portfolio for the authenticated user."""
    try:
        portfolio = await ctx.repo.create_portfolio(ctx.user_id, payload.name, payload.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    log.info("portfolio.created", user_id=str(ctx.user_id), name=payload.name)
    return PortfolioSummary(**portfolio_summary_fn(portfolio))


@router.get("/{portfolio_id}", response_model=PortfolioSummary)
async def portfolio_summary_endpoint(
    portfolio_id: UUID, ctx: Ctx = Depends(get_ctx)
) -> PortfolioSummary:
    """Return aggregate stats for a single portfolio."""
    try:
        portfolio = await ctx.repo.get_portfolio(ctx.user_id, portfolio_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    return PortfolioSummary(**portfolio_summary_fn(portfolio))


@router.patch("/{portfolio_id}", response_model=PortfolioSummary)
async def update_portfolio(
    portfolio_id: UUID, payload: PortfolioUpdate, ctx: Ctx = Depends(get_ctx)
) -> PortfolioSummary:
    try:
        portfolio = await ctx.repo.update_portfolio(
            ctx.user_id, portfolio_id, payload.name, payload.description
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return PortfolioSummary(**portfolio_summary_fn(portfolio))


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(portfolio_id: UUID, ctx: Ctx = Depends(get_ctx)) -> Response:
    """Delete an *empty* portfolio. Trade history is never deleted."""
    try:
        await ctx.repo.delete_portfolio(ctx.user_id, portfolio_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)

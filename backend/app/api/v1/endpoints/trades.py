"""Trade endpoints — add / list / close trades for a portfolio."""

from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.portfolio import TradeClose, TradeCreate, TradeOut
from app.services.portfolio import (
    Trade,
    store as portfolio_store,
    trade_breakdown as portfolio_trade_breakdown,
)
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

router = APIRouter()
log = get_logger(__name__)


def _resolve_user_uuid(raw: str) -> UUID:
    try:
        return UUID(raw)
    except (ValueError, AttributeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, raw)


@router.get("/{portfolio_id}", response_model=list[TradeOut])
async def list_trades(
    portfolio_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
) -> list[TradeOut]:
    """List all trades for a single portfolio."""
    user_uuid = _resolve_user_uuid(current_user.user_id)
    try:
        trades = portfolio_store.list_trades(user_uuid, portfolio_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    return [TradeOut(**row) for row in portfolio_trade_breakdown(trades)]


@router.post("", response_model=TradeOut, status_code=status.HTTP_201_CREATED)
async def add_trade(
    payload: TradeCreate,
    current_user: CurrentUser = Depends(get_current_user),
) -> TradeOut:
    """Append a new trade to the user's portfolio."""
    user_uuid = _resolve_user_uuid(current_user.user_id)
    trade = Trade(
        id=UUID(int=0),
        user_id=user_uuid,
        portfolio_id=payload.portfolio_id,
        symbol=normalize_symbol(payload.symbol),
        trade_type=payload.trade_type,
        direction=payload.direction,
        entry_price=payload.entry_price,
        exit_price=None,
        quantity=payload.quantity,
        entry_date=payload.entry_date,
        exit_date=None,
        notes=payload.notes,
    )
    try:
        stored = portfolio_store.add_trade(trade)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc

    log.info(
        "trade.added",
        user_id=current_user.user_id,
        trade_id=str(stored.id),
        symbol=stored.symbol,
    )
    return TradeOut(**portfolio_trade_breakdown([stored])[0])


@router.post("/{trade_id}/close", response_model=TradeOut)
async def close_trade(
    trade_id: UUID,
    payload: TradeClose,
    current_user: CurrentUser = Depends(get_current_user),
) -> TradeOut:
    """Close an open trade at ``payload.exit_price``."""
    user_uuid = _resolve_user_uuid(current_user.user_id)
    for portfolio in portfolio_store.list_portfolios(user_uuid):
        for trade in portfolio.trades:
            if trade.id == trade_id:
                trade.exit_price = payload.exit_price
                trade.exit_date = payload.exit_date
                log.info(
                    "trade.closed",
                    user_id=current_user.user_id,
                    trade_id=str(trade_id),
                )
                return TradeOut(**portfolio_trade_breakdown([trade])[0])
    raise HTTPException(status_code=404, detail="Trade not found")

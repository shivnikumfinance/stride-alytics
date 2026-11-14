"""Trade endpoints — add / list / export / close trades."""

from __future__ import annotations

from dataclasses import asdict
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import Ctx, get_ctx, to_csv
from app.api.v1.endpoints.gate import is_backdated
from app.api.v1.schemas.portfolio import TradeClose, TradeCreate, TradeNotes, TradeOut, TradePage
from app.repositories.sql import InvalidInput
from app.services.portfolio import Trade, trade_breakdown
from app.services.symbol_data import SymbolDataProvider, get_symbol_data_provider
from app.services.trading import entry_gate, load_account, log_gate_decision
from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

router = APIRouter()
log = get_logger(__name__)

TRADE_CSV_COLUMNS = [
    "trade_id",
    "portfolio_id",
    "symbol",
    "trade_type",
    "direction",
    "quantity",
    "entry_price",
    "exit_price",
    "entry_date",
    "exit_date",
    "pnl",
    "strike",
    "expiry",
    "strategy",
    "layer",
    "band",
    "risk_amount",
    "credit",
    "notes",
]


@router.get("", response_model=TradePage)
async def list_all_trades(
    portfolio_id: UUID | None = None,
    status_filter: Literal["open", "closed"] | None = Query(default=None, alias="status"),
    symbol: str | None = Query(default=None, max_length=10),
    sort: str = Query(
        default="-entry_date", description="entry_date | symbol | created_at; '-' = desc"
    ),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    ctx: Ctx = Depends(get_ctx),
) -> TradePage:
    """All of the user's trades, filtered, sorted and paginated."""
    try:
        trades, total = await ctx.repo.list_trades(
            ctx.user_id,
            portfolio_id=portfolio_id,
            status=status_filter,
            symbol=symbol,
            sort=sort,
            limit=limit,
            offset=offset,
        )
    except InvalidInput as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return TradePage(
        data=[TradeOut(**row) for row in trade_breakdown(trades)],
        total=total,
        limit=limit,
        offset=offset,
    )


# NOTE: declared before ``/{portfolio_id}`` so "export.csv" is not parsed as an id.
@router.get("/export.csv")
async def export_trades(portfolio_id: UUID | None = None, ctx: Ctx = Depends(get_ctx)) -> Response:
    """CSV export of every trade (FR-220, monthly audit export)."""
    trades, _ = await ctx.repo.list_trades(
        ctx.user_id, portfolio_id=portfolio_id, limit=10_000, sort="entry_date"
    )
    body = to_csv(TRADE_CSV_COLUMNS, trade_breakdown(trades))
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="trades.csv"'},
    )


@router.get("/{portfolio_id}", response_model=list[TradeOut])
async def list_trades(portfolio_id: UUID, ctx: Ctx = Depends(get_ctx)) -> list[TradeOut]:
    """List all trades for a single portfolio."""
    try:
        await ctx.repo.get_portfolio(ctx.user_id, portfolio_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    trades, _ = await ctx.repo.list_trades(
        ctx.user_id, portfolio_id=portfolio_id, sort="entry_date", limit=10_000
    )
    return [TradeOut(**row) for row in trade_breakdown(trades)]


@router.post("", response_model=TradeOut, status_code=status.HTTP_201_CREATED)
async def add_trade(
    payload: TradeCreate,
    ctx: Ctx = Depends(get_ctx),
    provider: SymbolDataProvider = Depends(get_symbol_data_provider),
) -> TradeOut:
    """Append a new trade to one of the user's portfolios.

    New entries pass through the Do-Not-Trade gate (unless switched off in Settings). A blocked
    entry is refused with 409 and every reason, and the decision is written to the signal log.
    Back-dated entries are record-keeping and are not gated.
    """
    symbol = normalize_symbol(payload.symbol)
    settings = await ctx.repo.get_settings(ctx.user_id)
    if settings["enforce_gate"]:
        if is_backdated(payload.entry_date):
            await ctx.repo.log_signal(
                ctx.user_id,
                kind="gate",
                decision="info",
                symbol=symbol,
                message="Gate skipped: back-dated entry (record-keeping).",
                details={"entry_date": payload.entry_date.isoformat()},
            )
        else:
            account = await load_account(ctx)
            result = await entry_gate(
                ctx,
                account,
                provider,
                symbol=symbol,
                trade_type=payload.trade_type,
                layer=payload.layer,
                strike=payload.strike,
                expiry=payload.expiry,
            )
            await log_gate_decision(
                ctx,
                symbol,
                result,
                {
                    "trade_type": payload.trade_type,
                    "layer": payload.layer,
                    "strike": payload.strike,
                    "expiry": payload.expiry.isoformat() if payload.expiry else None,
                },
            )
            if not result.clear:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Trade blocked by Do-Not-Trade rules",
                        "reasons": [asdict(r) for r in result.reasons],
                    },
                )

    trade = Trade(
        id=uuid4(),
        user_id=ctx.user_id,
        portfolio_id=payload.portfolio_id,
        symbol=symbol,
        trade_type=payload.trade_type,
        direction=payload.direction,
        entry_price=payload.entry_price,
        exit_price=None,
        quantity=payload.quantity,
        entry_date=payload.entry_date,
        exit_date=None,
        notes=payload.notes,
        strike=payload.strike,
        expiry=payload.expiry,
        strategy=payload.strategy,
        layer=payload.layer,
        band=payload.band,
        risk_amount=payload.risk_amount,
        credit=payload.credit,
    )
    try:
        stored = await ctx.repo.add_trade(trade)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Portfolio not found") from exc
    log.info("trade.added", user_id=str(ctx.user_id), trade_id=str(stored.id), symbol=stored.symbol)
    return TradeOut(**trade_breakdown([stored])[0])


@router.patch("/{trade_id}", response_model=TradeOut)
async def update_trade_notes(
    trade_id: UUID, payload: TradeNotes, ctx: Ctx = Depends(get_ctx)
) -> TradeOut:
    """Edit a trade's notes. Prices and dates are never edited; history is immutable."""
    try:
        trade = await ctx.repo.update_trade_notes(ctx.user_id, trade_id, payload.notes)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Trade not found") from exc
    return TradeOut(**trade_breakdown([trade])[0])


@router.post("/{trade_id}/close", response_model=TradeOut)
async def close_trade(trade_id: UUID, payload: TradeClose, ctx: Ctx = Depends(get_ctx)) -> TradeOut:
    """Close an open trade at ``payload.exit_price``."""
    try:
        trade = await ctx.repo.close_trade(
            ctx.user_id, trade_id, payload.exit_price, payload.exit_date
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Trade not found") from exc
    except InvalidInput as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:  # already closed
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    log.info("trade.closed", user_id=str(ctx.user_id), trade_id=str(trade_id))
    return TradeOut(**trade_breakdown([trade])[0])

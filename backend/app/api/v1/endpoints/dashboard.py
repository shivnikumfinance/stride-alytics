"""Home hub summary: metric cards plus the four core sections (FR-1010, FR-1020)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import Ctx, get_ctx
from app.domain.alerts import rank, summarize
from app.domain.allocation import growth_locked, layer_split
from app.domain.ev import rank_picks
from app.services.position_data import PositionDataProvider, get_position_data_provider
from app.services.positions import annotate_acks, evaluate_open_positions
from app.services.trading import load_account

router = APIRouter()

TOP_N = 3


@router.get("/summary")
async def summary(
    ctx: Ctx = Depends(get_ctx),
    provider: PositionDataProvider = Depends(get_position_data_provider),
) -> dict[str, Any]:
    """Everything the Home screen shows, in one call.

    * **Portfolio value** = account size + realised P&L + unrealised P&L of positions that could
      be priced (``unrealized_complete`` says whether all of them could).
    * **Options buying power** = equity − capital at risk in open trades. There is no margin data,
      so this is also the cash available. **Utilisation** = capital at risk / equity.
    """
    account = await load_account(ctx)
    alerts = await evaluate_open_positions(ctx, provider, account.regime.score)
    dicts, unacknowledged = await annotate_acks(ctx, alerts)

    settings = account.settings
    committed = await ctx.repo.open_committed(ctx.user_id)
    realized = round(account.equity - settings["account_size"], 2)
    priced = [a for a in alerts if a.pnl is not None]
    unrealized = round(sum(a.pnl for a in priced if a.pnl is not None), 2)
    buying_power = round(max(0.0, account.equity - committed), 2)
    state = account.regime.state

    all_picks, picks_week = await ctx.repo.list_picks(limit=20)
    picks = rank_picks(all_picks)[:TOP_N]
    return {
        "success": True,
        "data": {
            "metrics": {
                "portfolio_value": round(account.equity + unrealized, 2),
                "cash_available": buying_power,
                "realized_pnl": realized,
                "unrealized_pnl": unrealized,
                "unrealized_complete": len(priced) == len(alerts),
                "open_trades": len(alerts),
                "options_buying_power": buying_power,
                "capital_at_risk": round(committed, 2),
                "utilization_pct": (
                    round(committed / account.equity * 100, 1) if account.equity > 0 else None
                ),
                "account_size": settings["account_size"],
            },
            "alerts": {
                "summary": summarize(alerts),
                "unacknowledged_critical": unacknowledged,
                "top": [d for d in dicts if rank(d["severity"]) >= 1][:TOP_N],
            },
            "holdings": [d for d in dicts][:TOP_N],
            "picks": {"week_of": picks_week, "top": picks},
            "regime": {
                "score": account.regime.score,
                "state": state,
                "layer_split": layer_split(state),
                "growth_locked": growth_locked(state),
            },
        },
    }

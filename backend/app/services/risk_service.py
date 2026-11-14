"""Portfolio risk and scenario inputs built from a user's open positions."""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any

from fastapi.concurrency import run_in_threadpool

from app.api.deps import Ctx
from app.domain.alerts import MarketInput, PositionInput
from app.domain.portfolio_risk import PositionRisk, calculate_portfolio_risk
from app.services.position_data import PositionDataProvider
from app.services.positions import _market, _to_input, evaluate_open_positions
from app.services.scenarios import Shock, run_scenario, spot_ladder
from app.services.sector_data import SectorProvider


async def _sector(provider: SectorProvider, symbol: str) -> str | None:
    try:
        return await run_in_threadpool(provider, symbol)
    except Exception:  # noqa: BLE001 - an unknown sector is reported as "Unknown"
        return None


async def build_portfolio_risk(
    ctx: Ctx,
    provider: PositionDataProvider,
    sectors: SectorProvider,
    *,
    equity: float,
    regime_score: float | None,
) -> dict[str, Any]:
    """Net delta, margin %, sector exposure and limit breaches for the open positions."""
    alerts = await evaluate_open_positions(ctx, provider, regime_score)
    symbols = sorted({a.symbol for a in alerts})
    found = await asyncio.gather(*[_sector(sectors, s) for s in symbols])
    by_symbol = dict(zip(symbols, found))

    positions = [
        PositionRisk(
            symbol=a.symbol,
            risk_amount=float(a.strategy_detail.get("risk_amount") or 0.0),
            sector=by_symbol.get(a.symbol),
            position_delta=a.position_delta,
            spot=a.spot,
        )
        for a in alerts
    ]
    risk = calculate_portfolio_risk(positions, equity).to_dict()
    risk["open_positions"] = len(alerts)
    risk["regime_score"] = regime_score
    return risk


async def positions_with_market(
    ctx: Ctx, provider: PositionDataProvider
) -> list[tuple[PositionInput, MarketInput]]:
    trades = await ctx.repo.open_trades(ctx.user_id)
    markets = await asyncio.gather(*[_market(provider, t) for t in trades])
    return [(_to_input(t), mk) for t, mk in zip(trades, markets)]


def run_user_scenario(
    positions: list[tuple[PositionInput, MarketInput]],
    *,
    spot_pct: float,
    iv_shift: float,
    days_forward: int,
    ladder: bool = True,
) -> dict[str, Any]:
    today = date.today()
    result = run_scenario(positions, Shock(spot_pct, iv_shift, days_forward), today=today)
    if ladder:
        result["ladder"] = spot_ladder(
            positions, today=today, iv_shift=iv_shift, days_forward=days_forward
        )
    return result

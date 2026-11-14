"""Evaluate a user's open positions (alerts, P&L, Greeks) and track acknowledgements."""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Any

from fastapi.concurrency import run_in_threadpool

from app.api.deps import Ctx
from app.domain.alerts import (
    MarketInput,
    PositionAlert,
    PositionInput,
    evaluate_position,
    rank,
)
from app.services.portfolio import Trade
from app.services.position_data import PositionDataProvider


def _to_input(t: Trade) -> PositionInput:
    return PositionInput(
        trade_id=str(t.id),
        symbol=t.symbol,
        trade_type=t.trade_type,
        direction=t.direction,
        quantity=t.quantity,
        entry_price=t.entry_price,
        strike=t.strike,
        expiry=t.expiry,
        layer=t.layer,
        band=t.band,
        risk_amount=t.risk_amount,
        credit=t.credit,
    )


async def _market(provider: PositionDataProvider, t: Trade) -> MarketInput:
    try:
        return await run_in_threadpool(
            provider, t.symbol, trade_type=t.trade_type, strike=t.strike, expiry=t.expiry
        )
    except Exception:  # noqa: BLE001 - a failed lookup must not break the page
        return MarketInput(available=False)


async def evaluate_open_positions(
    ctx: Ctx, provider: PositionDataProvider, regime_score: float | None
) -> list[PositionAlert]:
    """One alert record per open trade, most urgent first."""
    trades = await ctx.repo.open_trades(ctx.user_id)
    # One lookup per distinct contract, in parallel.
    keys = {(t.symbol, t.trade_type, t.strike, t.expiry): t for t in trades}
    results = await asyncio.gather(*[_market(provider, t) for t in keys.values()])
    markets = dict(zip(keys.keys(), results))

    today = date.today()
    alerts = [
        evaluate_position(
            _to_input(t),
            markets[(t.symbol, t.trade_type, t.strike, t.expiry)],
            today=today,
            regime_score=regime_score,
        )
        for t in trades
    ]
    return sorted(alerts, key=lambda a: (-rank(a.severity), a.dte if a.dte is not None else 9999))


async def annotate_acks(ctx: Ctx, alerts: list[PositionAlert]) -> tuple[list[dict[str, Any]], int]:
    """Alert dicts with per-reason ``acknowledged`` flags, and the count still needing an ack.

    Stale acknowledgements (alert no longer firing, or trade closed) are resolved here, so a
    recurrence must be acknowledged again (BR-098).
    """
    ackable = {(a.trade_id, r.code) for a in alerts for r in a.reasons if rank(r.severity) >= 2}
    await ctx.repo.resolve_stale_acks(ctx.user_id, ackable)
    acked = await ctx.repo.active_acks(ctx.user_id)

    out: list[dict[str, Any]] = []
    needing = 0
    for a in alerts:
        d = a.to_dict()
        needs_ack = False
        for r in d["reasons"]:
            if rank(r["severity"]) >= 2:
                r["acknowledged"] = (a.trade_id, r["code"]) in acked
                needs_ack = needs_ack or (r["severity"] == "critical" and not r["acknowledged"])
            else:
                r["acknowledged"] = None
        d["unacknowledged_critical"] = needs_ack
        needing += int(needs_ack)
        out.append(d)
    return out, needing


def assignment_alarm_count(alerts: list[PositionAlert]) -> int | None:
    """Alarms for DNT rule BR-011. ``None`` = could not be verified (not evaluated, not blocking).

    Verified alarms always count. Otherwise, any open option position whose prices could not be
    fetched makes the answer unknown rather than "zero".
    """
    verified = sum(1 for a in alerts if a.assignment_risk)
    if verified:
        return verified
    unverified = any(a.trade_type != "stock" and not a.data_available for a in alerts)
    return None if unverified else 0

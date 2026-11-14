"""Glue between the pure rules (``app.domain``), live data, and one user's settings and trades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from fastapi.concurrency import run_in_threadpool

from app.api.deps import Ctx
from app.domain import gate as g
from app.domain.regime_score import RegimeScore
from app.services import regime_service
from app.services.position_data import PositionDataProvider
from app.services.positions import assignment_alarm_count, evaluate_open_positions
from app.services.symbol_data import SymbolDataProvider


@dataclass
class Account:
    settings: dict[str, Any]
    regime: RegimeScore
    equity: float
    # Open trades with an assignment alarm (BR-011); None = could not be verified.
    assignment_alarms: int | None = None


async def load_account(ctx: Ctx, position_provider: PositionDataProvider | None = None) -> Account:
    """The user's settings, their (weighted) regime score, and current equity.

    With a ``position_provider`` it also counts open positions with an assignment alarm so the
    gate can apply BR-011.
    """
    settings = await ctx.repo.get_settings(ctx.user_id)
    regime = await run_in_threadpool(regime_service.current_regime, settings["regime_weights"])
    equity = settings["account_size"] + await ctx.repo.realized_pnl(ctx.user_id)
    alarms: int | None = None
    if position_provider is not None:
        alerts = await evaluate_open_positions(ctx, position_provider, regime.score)
        alarms = assignment_alarm_count(alerts)
    return Account(
        settings=settings, regime=regime, equity=round(equity, 2), assignment_alarms=alarms
    )


def master_gate(account: Account) -> g.GateResult:
    return g.evaluate_master(
        account.regime,
        equity=account.equity,
        min_equity=account.settings["min_equity"],
        assignment_alarms=account.assignment_alarms,
    )


async def entry_gate(
    ctx: Ctx,
    account: Account,
    provider: SymbolDataProvider,
    *,
    symbol: str,
    trade_type: str,
    layer: str | None,
    strike: float | None,
    expiry: date | None,
) -> g.GateResult:
    """Full gate for a new entry (master + symbol + layer lock)."""
    option_type = trade_type if trade_type in ("call", "put") else None
    data = await run_in_threadpool(
        provider,
        symbol,
        trade_type=trade_type,
        strike=strike,
        expiry=expiry,
        option_type=option_type,
    )
    flags = await ctx.repo.get_symbol_flags(ctx.user_id, [symbol])
    news_flag = bool(flags.get(symbol.upper(), {}).get("news_flag", False))
    return g.evaluate_entry(
        regime=account.regime,
        equity=account.equity,
        min_equity=account.settings["min_equity"],
        symbol_data=data,
        trade_type=trade_type,
        layer=layer,
        news_flag=news_flag,
        today=date.today(),
        assignment_alarms=account.assignment_alarms,
    )


async def log_gate_decision(
    ctx: Ctx, symbol: str, result: g.GateResult, details: dict[str, Any]
) -> None:
    """Write the decision to the append-only signal log (BR-061): one row per blocking rule."""
    if result.clear:
        await ctx.repo.log_signal(
            ctx.user_id,
            kind="gate",
            decision="allowed",
            symbol=symbol,
            message="All Do-Not-Trade rules passed.",
            details={**details, "checked": result.checked, "not_evaluated": result.not_evaluated},
        )
        return
    for reason in result.reasons:
        await ctx.repo.log_signal(
            ctx.user_id,
            kind="gate",
            decision="blocked",
            symbol=symbol,
            rule_id=reason.rule_id,
            message=reason.message,
            details={**details, "reason_kind": reason.kind},
        )

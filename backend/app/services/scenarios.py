"""Scenario / stress simulation (docs: FR-530).

Reprices every open position under a shock to the underlying price, implied volatility and time,
using Black-Scholes (European-style; listed equity options are American, which is close enough
for a stress test). Pure and offline: market inputs are passed in. A position that cannot be
priced (no spot, or no implied volatility for an option) is reported as such and left out of the
totals, never assumed to be unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.domain.alerts import CONTRACT_MULTIPLIER, MarketInput, PositionInput
from app.services.greeks import calculate_option_price
from app.utils.constants import DEFAULT_RISK_FREE_RATE

MIN_TIME = 1 / 365 / 24  # one hour; avoids a zero-time division right at expiry


@dataclass(frozen=True)
class Shock:
    spot_pct: float = 0.0  # +10 means the underlying rises 10%
    iv_shift: float = 0.0  # +0.05 means implied volatility rises 5 points
    days_forward: int = 0


def _scale(pos: PositionInput) -> int:
    return CONTRACT_MULTIPLIER if pos.trade_type in ("call", "put") else 1


def _option_value(pos: PositionInput, spot: float, iv: float, days_left: float) -> float:
    """Per-share value of the option under the given inputs (intrinsic value at/after expiry)."""
    assert pos.strike is not None
    if days_left <= 0:
        intrinsic = spot - pos.strike if pos.trade_type == "call" else pos.strike - spot
        return max(intrinsic, 0.0)
    return calculate_option_price(
        spot,
        pos.strike,
        max(days_left / 365.0, MIN_TIME),
        DEFAULT_RISK_FREE_RATE,
        iv,
        pos.trade_type,
    )


def reprice_position(
    pos: PositionInput, market: MarketInput, shock: Shock, *, today: date
) -> dict[str, Any]:
    """Current vs shocked P&L of one position. ``priced`` is False when it cannot be computed."""
    base = {
        "trade_id": pos.trade_id,
        "symbol": pos.symbol,
        "trade_type": pos.trade_type,
        "direction": pos.direction,
        "quantity": pos.quantity,
        "priced": False,
        "current_pnl": None,
        "scenario_pnl": None,
        "change": None,
    }
    if not market.available or market.spot is None or market.spot <= 0:
        return {**base, "reason": "no market data"}

    sign = -1 if pos.direction == "short" else 1  # P&L per share = sign * (value - entry)
    new_spot = market.spot * (1 + shock.spot_pct / 100.0)
    if new_spot <= 0:
        return {**base, "reason": "shock takes the price to zero or below"}

    if pos.trade_type == "stock":
        current_value, new_value = market.spot, new_spot
    else:
        if not pos.strike or not pos.expiry:
            return {**base, "reason": "no strike or expiry"}
        iv = market.iv
        if iv is None or iv <= 0:
            return {**base, "reason": "no implied volatility"}
        days_now = (pos.expiry - today).days
        new_iv = max(iv + shock.iv_shift, 0.01)
        model_now = _option_value(pos, market.spot, iv, days_now)
        current_value = market.mark if market.mark is not None else model_now
        days_left = days_now - shock.days_forward
        new_value = _option_value(pos, new_spot, new_iv, days_left)
        if days_left > 0 and market.mark is not None:
            # Apply the model's *change* to the market mark, so a zero shock changes nothing
            # even when the mark differs from the model price.
            new_value = max(market.mark + (new_value - model_now), 0.0)

    qty = pos.quantity * _scale(pos)
    current_pnl = round(sign * (current_value - pos.entry_price) * qty, 2)
    scenario_pnl = round(sign * (new_value - pos.entry_price) * qty, 2)
    return {
        **base,
        "priced": True,
        "current_pnl": current_pnl,
        "scenario_pnl": scenario_pnl,
        "change": round(scenario_pnl - current_pnl, 2),
    }


def run_scenario(
    positions: list[tuple[PositionInput, MarketInput]], shock: Shock, *, today: date
) -> dict[str, Any]:
    rows = [reprice_position(p, m, shock, today=today) for p, m in positions]
    priced = [r for r in rows if r["priced"]]
    return {
        "shock": {
            "spot_pct": shock.spot_pct,
            "iv_shift": shock.iv_shift,
            "days_forward": shock.days_forward,
        },
        "positions": rows,
        "total_change": round(sum(r["change"] for r in priced), 2),
        "total_scenario_pnl": round(sum(r["scenario_pnl"] for r in priced), 2),
        "priced": len(priced),
        "unpriced": len(rows) - len(priced),
    }


LADDER_STEPS = (-20.0, -10.0, -5.0, 0.0, 5.0, 10.0, 20.0)


def spot_ladder(
    positions: list[tuple[PositionInput, MarketInput]],
    *,
    today: date,
    steps: tuple[float, ...] = LADDER_STEPS,
    iv_shift: float = 0.0,
    days_forward: int = 0,
) -> list[dict[str, float]]:
    """Total scenario change across a range of price moves (for the P&L curve chart)."""
    out = []
    for pct in steps:
        res = run_scenario(positions, Shock(pct, iv_shift, days_forward), today=today)
        out.append({"spot_pct": pct, "total_change": res["total_change"]})
    return out

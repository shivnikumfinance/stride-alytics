"""Portfolio & trade domain objects and analytics (pure functions).

Storage lives in ``app.repositories.sql.Repo``; this module has no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable
from uuid import UUID

from app.utils.validators import normalize_symbol

# ---------- Domain models ----------


@dataclass
class Trade:
    id: UUID
    user_id: UUID
    portfolio_id: UUID
    symbol: str
    trade_type: str  # 'call' | 'put' | 'stock'
    direction: str  # 'long' | 'short'
    entry_price: float
    exit_price: float | None
    quantity: int
    entry_date: date | None
    exit_date: date | None
    notes: str | None = None
    # Option/strategy detail (needed for DTE, Greeks, risk and band caps)
    strike: float | None = None
    expiry: date | None = None
    strategy: str | None = None
    layer: str | None = None  # 'base' | 'growth'
    band: str | None = None  # 'A'..'E'
    risk_amount: float | None = None
    credit: float | None = None


@dataclass
class Portfolio:
    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    trades: list[Trade] = field(default_factory=list)


# ---------- Analytics ----------


def calculate_pnl(trade: Trade) -> float:
    if trade.exit_price is None:
        return 0.0
    raw = (trade.exit_price - trade.entry_price) * trade.quantity
    return -raw if trade.direction == "short" else raw


def portfolio_summary(portfolio: Portfolio) -> dict[str, Any]:
    trades = portfolio.trades
    closed = [t for t in trades if t.exit_price is not None]
    open_trades = [t for t in trades if t.exit_price is None]

    total_pnl = sum(calculate_pnl(t) for t in closed)
    winners = [t for t in closed if calculate_pnl(t) > 0]
    losers = [t for t in closed if calculate_pnl(t) < 0]
    win_rate = (len(winners) / len(closed)) if closed else 0.0

    return {
        "portfolio_id": str(portfolio.id),
        "name": portfolio.name,
        "total_trades": len(trades),
        "open_trades": len(open_trades),
        "closed_trades": len(closed),
        "total_pnl": round(total_pnl, 2),
        "win_rate": round(win_rate, 3),
        "winners": len(winners),
        "losers": len(losers),
    }


def portfolio_trade_breakdown(trades: Iterable[Trade]) -> list[dict[str, Any]]:
    out = []
    for t in trades:
        entry = t.entry_date or date.today()
        out.append(
            {
                "trade_id": str(t.id),
                "portfolio_id": str(t.portfolio_id),
                "symbol": normalize_symbol(t.symbol),
                "trade_type": t.trade_type,
                "direction": t.direction,
                "quantity": t.quantity,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "entry_date": entry.isoformat(),
                "exit_date": t.exit_date.isoformat() if t.exit_date else None,
                "pnl": round(calculate_pnl(t), 2),
                "open": t.exit_price is None,
                "notes": t.notes,
                "strike": t.strike,
                "expiry": t.expiry.isoformat() if t.expiry else None,
                "strategy": t.strategy,
                "layer": t.layer,
                "band": t.band,
                "risk_amount": t.risk_amount,
                "credit": t.credit,
            }
        )
    return out


# --- Convenience aliases so endpoint imports stay short and explicit ---
summary = portfolio_summary
trade_breakdown = portfolio_trade_breakdown

"""Portfolio & trade analytics — pure functions over user-scoped data.

Phase 1 keeps the implementation synchronous and in-memory (a dict keyed
by ``user_id``) so endpoints are testable without a Supabase connection.
Phase 2 will swap the in-memory store for SQLAlchemy/Postgres queries
that automatically respect the ``portfolios`` / ``trades`` RLS policies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable
from uuid import UUID, uuid4

from app.utils.logger import get_logger
from app.utils.validators import normalize_symbol

log = get_logger(__name__)


# ---------- Domain models ----------


@dataclass
class Trade:
    id: UUID
    user_id: UUID
    portfolio_id: UUID
    symbol: str
    trade_type: str         # 'call' | 'put' | 'stock'
    direction: str          # 'long' | 'short'
    entry_price: float
    exit_price: float | None
    quantity: int
    entry_date: date
    exit_date: date | None
    notes: str | None = None


@dataclass
class Portfolio:
    id: UUID
    user_id: UUID
    name: str
    description: str | None = None
    trades: list[Trade] = field(default_factory=list)


# ---------- In-memory store (replace with DB in Phase 2) ----------


class PortfolioStore:
    def __init__(self) -> None:
        self._portfolios: dict[UUID, Portfolio] = {}

    # --- Portfolios ---
    def create_portfolio(self, user_id: UUID, name: str, description: str | None = None) -> Portfolio:
        for p in self._portfolios.values():
            if p.user_id == user_id and p.name == name:
                raise ValueError(f"portfolio named {name!r} already exists for this user")
        portfolio = Portfolio(id=uuid4(), user_id=user_id, name=name, description=description)
        self._portfolios[portfolio.id] = portfolio
        return portfolio

    def list_portfolios(self, user_id: UUID) -> list[Portfolio]:
        return [p for p in self._portfolios.values() if p.user_id == user_id]

    def get_portfolio(self, user_id: UUID, portfolio_id: UUID) -> Portfolio:
        p = self._portfolios.get(portfolio_id)
        if p is None or p.user_id != user_id:
            raise KeyError("portfolio not found")
        return p

    # --- Trades ---
    def add_trade(self, trade: Trade) -> Trade:
        portfolio = self.get_portfolio(trade.user_id, trade.portfolio_id)
        trade.id = trade.id or uuid4()
        portfolio.trades.append(trade)
        return trade

    def list_trades(self, user_id: UUID, portfolio_id: UUID) -> list[Trade]:
        return list(self.get_portfolio(user_id, portfolio_id).trades)


# Singleton store — replace with a real DB session per-request in Phase 2.
store = PortfolioStore()


# ---------- Analytics ----------


def calculate_pnl(trade: Trade) -> float:
    if trade.exit_price is None:
        return 0.0
    raw = (trade.exit_price - trade.entry_price) * trade.quantity
    return -raw if trade.direction == "short" else raw


def portfolio_summary(portfolio: Portfolio) -> dict:
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


def portfolio_trade_breakdown(trades: Iterable[Trade]) -> list[dict]:
    out = []
    for t in trades:
        # Default entry_date to today if not set (dev-token / in-memory path).
        entry = t.entry_date or date.today()
        out.append(
            {
                "trade_id": str(t.id),
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
            }
        )
    return out


# --- Convenience aliases so endpoint imports stay short and explicit ---
portfolio_store = store
summary = portfolio_summary
trade_breakdown = portfolio_trade_breakdown


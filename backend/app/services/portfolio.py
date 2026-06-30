"""Portfolio & trade analytics — pure functions over user-scoped data.

Phase 1 kept the implementation synchronous and in-memory (a dict keyed
by ``user_id``). Phase 2 now uses SQLAlchemy/Postgres queries via the
``get_session`` dependency.

For backward compatibility during tests, we keep the in-memory ``PortfolioStore``
and expose ``reset_store`` so pytest can toggle between storage back-ends.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable
from uuid import UUID, uuid4

from sqlalchemy import text

from app.database import get_session
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
    trade_type: str  # 'call' | 'put' | 'stock'
    direction: str  # 'long' | 'short'
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


# ---------- In-memory store (fallback for dev/tests) ----------


class PortfolioStore:
    def __init__(self) -> None:
        self._portfolios: dict[UUID, Portfolio] = {}
        self._use_db = False

    def enable_db(self) -> None:
        """Switch to PostgreSQL-backed storage."""
        self._use_db = True

    # --- Portfolios ---
    def create_portfolio(
        self, user_id: UUID, name: str, description: str | None = None
    ) -> Portfolio:
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

    # --- DB-backed helpers (Phase 2) ---

    async def create_portfolio_db(
        self, user_id: str, name: str, description: str | None = None
    ) -> dict[str, Any]:
        """Insert a portfolio row via SQLAlchemy and return the row dict."""
        async with get_session() as session:
            result = await session.execute(
                text("""
                    INSERT INTO portfolios (user_id, name, description)
                    VALUES (:user_id, :name, :description)
                    RETURNING id, user_id, name, description, created_at
                """),
                {"user_id": user_id, "name": name, "description": description},
            )
            await session.commit()
            row = result.mappings().one()
            return dict(row)

    async def list_portfolios_db(self, user_id: str) -> list[dict[str, Any]]:
        """List portfolios from the database."""
        async with get_session() as session:
            result = await session.execute(
                text(
                    "SELECT id, user_id, name, description, created_at FROM portfolios WHERE user_id = :uid ORDER BY created_at DESC"
                ),
                {"uid": user_id},
            )
            rows = result.mappings().all()
            return [dict(r) for r in rows]

    async def get_portfolio_summary_db(
        self, portfolio_id: UUID, user_id: str
    ) -> dict[str, Any] | None:
        """Return aggregate stats for a portfolio using the portfolio_summary view."""
        async with get_session() as session:
            result = await session.execute(
                text("SELECT * FROM portfolio_summary WHERE id = :pid AND user_id = :uid"),
                {"pid": str(portfolio_id), "uid": user_id},
            )
            row = result.mappings().one_or_none()
            if row is None:
                return None
            return dict(row)

    async def add_trade_db(self, trade_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a trade row and return it."""
        async with get_session() as session:
            result = await session.execute(
                text("""
                    INSERT INTO trades (user_id, portfolio_id, symbol, trade_type, direction,
                                        entry_price, quantity, entry_date, notes)
                    VALUES (:user_id, :portfolio_id, :symbol, :trade_type, :direction,
                            :entry_price, :quantity, :entry_date, :notes)
                    RETURNING id, user_id, portfolio_id, symbol, trade_type, direction,
                              entry_price, exit_price, quantity, entry_date, exit_date, notes
                """),
                trade_data,
            )
            await session.commit()
            row = result.mappings().one()
            return dict(row)

    async def close_trade_db(
        self, trade_id: str, user_id: str, exit_price: float, exit_date: date
    ) -> dict[str, Any] | None:
        """Close a trade by setting exit_price and exit_date."""
        async with get_session() as session:
            result = await session.execute(
                text("""
                    UPDATE trades
                    SET exit_price = :exit_price, exit_date = :exit_date, updated_at = now()
                    WHERE id = :trade_id AND user_id = :user_id AND exit_price IS NULL
                    RETURNING id, user_id, portfolio_id, symbol, trade_type, direction,
                              entry_price, exit_price, quantity, entry_date, exit_date
                """),
                {
                    "trade_id": trade_id,
                    "user_id": user_id,
                    "exit_price": exit_price,
                    "exit_date": exit_date.isoformat(),
                },
            )
            await session.commit()
            row = result.mappings().one_or_none()
            if row is None:
                return None
            return dict(row)


# Singleton store
store = PortfolioStore()


def reset_store() -> None:
    """Clear the in-memory store (used by pytest)."""
    store._portfolios.clear()


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

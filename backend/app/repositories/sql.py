"""SQLAlchemy repository (PostgreSQL in production, SQLite in dev/tests).

Conventions
-----------
* Every method is scoped to ``user_id``; another user's rows behave as "not found".
* ``KeyError`` = not found, ``ValueError`` = rule violation (duplicate, already closed, ...).
  Endpoints translate these to 404 / 409 / 422.
* Public write methods commit. Audit rows are written in the *same* transaction as the
  change they describe, so a change can never exist without its audit record.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models as m
from app.services.portfolio import Portfolio, Trade


class InvalidInput(ValueError):
    """The request is well-formed but not acceptable (endpoints map it to 422)."""


_TRADE_SORTS = {"entry_date", "symbol", "created_at"}
SETTINGS_FIELDS = (
    "notify_weekly_picks",
    "notify_market_regime",
    "default_symbol",
    "theme",
    "screener_preset",
    "account_size",
    "base_risk_pct",
    "growth_risk_pct",
    "min_equity",
    "band_caps",
    "regime_weights",
    "widget_toggles",
    "enforce_gate",
)


# ---------- helpers ----------


def _num(value: Decimal | float | None) -> float | None:
    return None if value is None else float(value)


def _iso(dt: datetime | None) -> str | None:
    """ISO-8601 in UTC. SQLite returns naive datetimes; they are always UTC here."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _as_dt(d: date | None) -> datetime | None:
    return None if d is None else datetime.combine(d, time.min, tzinfo=timezone.utc)


def _as_date(dt: datetime | date | None) -> date | None:
    if dt is None:
        return None
    return dt.date() if isinstance(dt, datetime) else dt


def _to_trade(row: m.Trade) -> Trade:
    return Trade(
        id=row.id,
        user_id=row.user_id,
        portfolio_id=row.portfolio_id,
        symbol=row.symbol,
        trade_type=row.trade_type,
        direction=row.direction,
        entry_price=float(row.entry_price),
        exit_price=_num(row.exit_price),
        quantity=row.quantity,
        entry_date=_as_date(row.entry_date),
        exit_date=_as_date(row.exit_date),
        notes=row.notes,
        strike=_num(row.strike),
        expiry=_as_date(row.expiry),
        strategy=row.strategy,
        layer=row.layer,
        band=row.band,
        risk_amount=_num(row.risk_amount),
        credit=_num(row.credit),
    )


def _to_portfolio(row: m.Portfolio, trades: list[m.Trade] | None = None) -> Portfolio:
    return Portfolio(
        id=row.id,
        user_id=row.user_id,
        name=row.name,
        description=row.description,
        trades=[_to_trade(t) for t in (trades if trades is not None else [])],
    )


def trade_snapshot(t: Trade) -> dict[str, Any]:
    """JSON-safe description of a trade for audit rows."""
    return {
        "symbol": t.symbol,
        "trade_type": t.trade_type,
        "direction": t.direction,
        "quantity": t.quantity,
        "entry_price": t.entry_price,
        "exit_price": t.exit_price,
        "entry_date": t.entry_date.isoformat() if t.entry_date else None,
        "exit_date": t.exit_date.isoformat() if t.exit_date else None,
        "strike": t.strike,
        "expiry": t.expiry.isoformat() if t.expiry else None,
        "strategy": t.strategy,
        "layer": t.layer,
        "band": t.band,
        "risk_amount": t.risk_amount,
        "credit": t.credit,
        "notes": t.notes,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class Repo:
    """All persistence for one request (one ``AsyncSession``)."""

    def __init__(self, session: AsyncSession) -> None:
        self.s = session

    # ------------------------------------------------------------------ users

    async def ensure_user(self, user_id: UUID, email: str | None) -> None:
        """Create the ``public.users`` row on first sight (Supabase signup does not)."""
        if await self.s.get(m.User, user_id) is not None:
            return
        address = email or f"{user_id}@local.invalid"
        self.s.add(m.User(id=user_id, email=address))
        try:
            await self.s.commit()
        except IntegrityError:
            await self.s.rollback()
            if await self.s.get(m.User, user_id) is not None:
                return  # created concurrently
            # The email belongs to a different id: keep ours unique without leaking the clash.
            self.s.add(m.User(id=user_id, email=f"{user_id}+{address}"))
            await self.s.commit()

    # ------------------------------------------------------------- portfolios

    async def create_portfolio(
        self, user_id: UUID, name: str, description: str | None = None
    ) -> Portfolio:
        exists = await self.s.scalar(
            select(m.Portfolio.id).where(m.Portfolio.user_id == user_id, m.Portfolio.name == name)
        )
        if exists is not None:
            raise ValueError(f"portfolio named {name!r} already exists for this user")
        row = m.Portfolio(user_id=user_id, name=name, description=description)
        self.s.add(row)
        await self.s.flush()
        self._audit(user_id, "portfolio.create", "portfolio", row.id, None, {"name": name})
        await self.s.commit()
        return _to_portfolio(row, [])

    async def list_portfolios(self, user_id: UUID) -> list[Portfolio]:
        rows = (
            await self.s.scalars(
                select(m.Portfolio)
                .where(m.Portfolio.user_id == user_id)
                .options(selectinload(m.Portfolio.trades))
                .order_by(m.Portfolio.created_at)
            )
        ).all()
        return [_to_portfolio(r, list(r.trades)) for r in rows]

    async def _portfolio_row(self, user_id: UUID, portfolio_id: UUID) -> m.Portfolio:
        row = await self.s.scalar(
            select(m.Portfolio)
            .where(m.Portfolio.id == portfolio_id, m.Portfolio.user_id == user_id)
            .options(selectinload(m.Portfolio.trades))
        )
        if row is None:
            raise KeyError("portfolio not found")
        return row

    async def get_portfolio(self, user_id: UUID, portfolio_id: UUID) -> Portfolio:
        row = await self._portfolio_row(user_id, portfolio_id)
        return _to_portfolio(row, list(row.trades))

    async def update_portfolio(
        self,
        user_id: UUID,
        portfolio_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Portfolio:
        row = await self._portfolio_row(user_id, portfolio_id)
        before = {"name": row.name, "description": row.description}
        if name is not None and name != row.name:
            clash = await self.s.scalar(
                select(m.Portfolio.id).where(
                    m.Portfolio.user_id == user_id,
                    m.Portfolio.name == name,
                    m.Portfolio.id != portfolio_id,
                )
            )
            if clash is not None:
                raise ValueError(f"portfolio named {name!r} already exists for this user")
            row.name = name
        if description is not None:
            row.description = description
        after = {"name": row.name, "description": row.description}
        self._audit(user_id, "portfolio.update", "portfolio", row.id, before, after)
        await self.s.commit()
        return _to_portfolio(row, list(row.trades))

    async def delete_portfolio(self, user_id: UUID, portfolio_id: UUID) -> None:
        row = await self._portfolio_row(user_id, portfolio_id)
        if row.trades:
            raise ValueError("portfolio still has trades; trade history is never deleted")
        self._audit(user_id, "portfolio.delete", "portfolio", row.id, {"name": row.name}, None)
        await self.s.delete(row)
        await self.s.commit()

    # ----------------------------------------------------------------- trades

    async def add_trade(self, trade: Trade) -> Trade:
        await self._portfolio_row(trade.user_id, trade.portfolio_id)  # KeyError if not theirs
        row = m.Trade(
            id=trade.id,
            user_id=trade.user_id,
            portfolio_id=trade.portfolio_id,
            symbol=trade.symbol,
            trade_type=trade.trade_type,
            direction=trade.direction,
            entry_price=trade.entry_price,
            quantity=trade.quantity,
            entry_date=_as_dt(trade.entry_date or date.today()),
            notes=trade.notes,
            strike=trade.strike,
            expiry=trade.expiry,
            strategy=trade.strategy,
            layer=trade.layer,
            band=trade.band,
            risk_amount=trade.risk_amount,
            credit=trade.credit,
        )
        self.s.add(row)
        await self.s.flush()
        created = _to_trade(row)
        self._audit(trade.user_id, "trade.add", "trade", row.id, None, trade_snapshot(created))
        await self.s.commit()
        return created

    async def _trade_row(self, user_id: UUID, trade_id: UUID) -> m.Trade:
        row = await self.s.scalar(
            select(m.Trade).where(m.Trade.id == trade_id, m.Trade.user_id == user_id)
        )
        if row is None:
            raise KeyError("trade not found")
        return row

    async def get_trade(self, user_id: UUID, trade_id: UUID) -> Trade:
        return _to_trade(await self._trade_row(user_id, trade_id))

    async def list_trades(
        self,
        user_id: UUID,
        *,
        portfolio_id: UUID | None = None,
        status: str | None = None,
        symbol: str | None = None,
        sort: str = "-entry_date",
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Trade], int]:
        cond = [m.Trade.user_id == user_id]
        if portfolio_id is not None:
            cond.append(m.Trade.portfolio_id == portfolio_id)
        if status == "open":
            cond.append(m.Trade.exit_price.is_(None))
        elif status == "closed":
            cond.append(m.Trade.exit_price.is_not(None))
        if symbol:
            cond.append(m.Trade.symbol == symbol.strip().upper())

        field_name = sort.lstrip("-+")
        if field_name not in _TRADE_SORTS:
            raise InvalidInput(f"cannot sort by {field_name!r}; allowed: {sorted(_TRADE_SORTS)}")
        column = getattr(m.Trade, field_name)
        order = column.desc() if sort.startswith("-") else column.asc()

        total = await self.s.scalar(select(func.count()).select_from(m.Trade).where(*cond)) or 0
        rows = (
            await self.s.scalars(
                select(m.Trade).where(*cond).order_by(order, m.Trade.id).limit(limit).offset(offset)
            )
        ).all()
        return [_to_trade(r) for r in rows], int(total)

    async def close_trade(
        self, user_id: UUID, trade_id: UUID, exit_price: float, exit_date: date
    ) -> Trade:
        row = await self._trade_row(user_id, trade_id)
        if row.exit_price is not None:
            raise ValueError("trade is already closed")
        entry = _as_date(row.entry_date)
        if entry is not None and exit_date < entry:
            raise InvalidInput("exit date is before the entry date")
        before = trade_snapshot(_to_trade(row))
        row.exit_price = exit_price
        row.exit_date = _as_dt(exit_date)
        await self.s.flush()
        closed = _to_trade(row)
        self._audit(user_id, "trade.close", "trade", row.id, before, trade_snapshot(closed))
        await self.s.commit()
        return closed

    async def update_trade_notes(self, user_id: UUID, trade_id: UUID, notes: str | None) -> Trade:
        row = await self._trade_row(user_id, trade_id)
        before = {"notes": row.notes}
        row.notes = notes
        await self.s.flush()
        self._audit(user_id, "trade.notes", "trade", row.id, before, {"notes": notes})
        await self.s.commit()
        return _to_trade(row)

    # -------------------------------------------------------------- watchlists

    async def _watchlist_row(self, user_id: UUID, watchlist_id: UUID) -> m.Watchlist:
        row = await self.s.scalar(
            select(m.Watchlist)
            .where(m.Watchlist.id == watchlist_id, m.Watchlist.user_id == user_id)
            .options(selectinload(m.Watchlist.items))
        )
        if row is None:
            raise KeyError("watchlist not found")
        return row

    @staticmethod
    def _watchlist_dict(row: m.Watchlist) -> dict[str, Any]:
        return {
            "id": str(row.id),
            "name": row.name,
            "symbols": [i.symbol for i in row.items],
            "created_at": _iso(row.created_at),
        }

    async def create_watchlist(
        self, user_id: UUID, name: str, symbols: list[str] | None = None
    ) -> dict[str, Any]:
        exists = await self.s.scalar(
            select(m.Watchlist.id).where(m.Watchlist.user_id == user_id, m.Watchlist.name == name)
        )
        if exists is not None:
            raise ValueError(f"watchlist named {name!r} already exists")
        row = m.Watchlist(user_id=user_id, name=name)
        for sym in dict.fromkeys(s.strip().upper() for s in (symbols or []) if s.strip()):
            row.items.append(m.WatchlistItem(symbol=sym))
        self.s.add(row)
        await self.s.flush()
        self._audit(user_id, "watchlist.create", "watchlist", row.id, None, {"name": name})
        await self.s.commit()
        return self._watchlist_dict(row)

    async def list_watchlists(self, user_id: UUID) -> list[dict[str, Any]]:
        rows = (
            await self.s.scalars(
                select(m.Watchlist)
                .where(m.Watchlist.user_id == user_id)
                .options(selectinload(m.Watchlist.items))
                .order_by(m.Watchlist.created_at)
            )
        ).all()
        return [self._watchlist_dict(r) for r in rows]

    async def get_watchlist(self, user_id: UUID, watchlist_id: UUID) -> dict[str, Any]:
        return self._watchlist_dict(await self._watchlist_row(user_id, watchlist_id))

    async def delete_watchlist(self, user_id: UUID, watchlist_id: UUID) -> None:
        row = await self._watchlist_row(user_id, watchlist_id)
        self._audit(user_id, "watchlist.delete", "watchlist", row.id, {"name": row.name}, None)
        await self.s.delete(row)
        await self.s.commit()

    async def add_symbol(self, user_id: UUID, watchlist_id: UUID, symbol: str) -> dict[str, Any]:
        row = await self._watchlist_row(user_id, watchlist_id)
        sym = symbol.strip().upper()
        if sym and sym not in {i.symbol for i in row.items}:
            row.items.append(m.WatchlistItem(symbol=sym))
            await self.s.flush()
            self._audit(user_id, "watchlist.add_symbol", "watchlist", row.id, None, {"symbol": sym})
            await self.s.commit()
        return self._watchlist_dict(row)

    async def remove_symbol(self, user_id: UUID, watchlist_id: UUID, symbol: str) -> dict[str, Any]:
        row = await self._watchlist_row(user_id, watchlist_id)
        sym = symbol.strip().upper()
        item = next((i for i in row.items if i.symbol == sym), None)
        if item is None:
            raise KeyError("symbol not in watchlist")
        row.items.remove(item)
        await self.s.flush()
        self._audit(user_id, "watchlist.remove_symbol", "watchlist", row.id, {"symbol": sym}, None)
        await self.s.commit()
        return self._watchlist_dict(row)

    # ------------------------------------------------------------ symbol flags

    async def set_symbol_flag(
        self, user_id: UUID, symbol: str, news_flag: bool, note: str | None = None
    ) -> dict[str, Any]:
        sym = symbol.strip().upper()
        row = await self.s.get(m.SymbolFlag, (user_id, sym))
        before = None if row is None else {"news_flag": row.news_flag, "note": row.note}
        if row is None:
            row = m.SymbolFlag(user_id=user_id, symbol=sym, news_flag=news_flag, note=note)
            self.s.add(row)
        else:
            row.news_flag = news_flag
            row.note = note
        await self.s.flush()
        self._audit(
            user_id,
            "symbol.flag",
            "symbol",
            sym,
            before,
            {"news_flag": news_flag, "note": note},
        )
        await self.s.commit()
        return {"symbol": sym, "news_flag": news_flag, "note": note}

    async def get_symbol_flags(
        self, user_id: UUID, symbols: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        query = select(m.SymbolFlag).where(m.SymbolFlag.user_id == user_id)
        if symbols:
            query = query.where(m.SymbolFlag.symbol.in_([s.strip().upper() for s in symbols]))
        rows = (await self.s.scalars(query)).all()
        return {r.symbol: {"news_flag": r.news_flag, "note": r.note} for r in rows}

    # ------------------------------------------------------------------- logs

    def _audit(
        self,
        user_id: UUID,
        action: str,
        entity: str,
        entity_id: Any,
        before: dict[str, Any] | None,
        after: dict[str, Any] | None,
    ) -> None:
        """Queue an audit row in the current transaction (committed with the change)."""
        self.s.add(
            m.AuditLog(
                user_id=user_id,
                action=action,
                entity=entity,
                entity_id=None if entity_id is None else str(entity_id),
                before=None if before is None else {k: _jsonable(v) for k, v in before.items()},
                after=None if after is None else {k: _jsonable(v) for k, v in after.items()},
            )
        )

    async def log_signal(
        self,
        user_id: UUID,
        *,
        kind: str,
        decision: str,
        symbol: str | None = None,
        rule_id: str | None = None,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.s.add(
            m.SignalLog(
                user_id=user_id,
                kind=kind,
                decision=decision,
                symbol=symbol.upper() if symbol else None,
                rule_id=rule_id,
                message=message,
                details=details or {},
            )
        )
        await self.s.commit()

    @staticmethod
    def _log_filters(model: Any, user_id: UUID, start: datetime | None, end: datetime | None):
        cond = [model.user_id == user_id]
        if start is not None:
            cond.append(model.occurred_at >= start)
        if end is not None:
            cond.append(model.occurred_at <= end)
        return cond

    async def list_signals(
        self,
        user_id: UUID,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        symbol: str | None = None,
        rule_id: str | None = None,
        decision: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        cond = self._log_filters(m.SignalLog, user_id, start, end)
        if symbol:
            cond.append(m.SignalLog.symbol == symbol.strip().upper())
        if rule_id:
            cond.append(m.SignalLog.rule_id == rule_id)
        if decision:
            cond.append(m.SignalLog.decision == decision)
        total = await self.s.scalar(select(func.count()).select_from(m.SignalLog).where(*cond))
        rows = (
            await self.s.scalars(
                select(m.SignalLog)
                .where(*cond)
                .order_by(m.SignalLog.occurred_at.desc(), m.SignalLog.id)
                .limit(limit)
                .offset(offset)
            )
        ).all()
        return [
            {
                "id": str(r.id),
                "occurred_at": _iso(r.occurred_at),
                "kind": r.kind,
                "symbol": r.symbol,
                "rule_id": r.rule_id,
                "decision": r.decision,
                "message": r.message,
                "details": r.details,
            }
            for r in rows
        ], int(total or 0)

    async def list_audit(
        self,
        user_id: UUID,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        entity: str | None = None,
        action: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        cond = self._log_filters(m.AuditLog, user_id, start, end)
        if entity:
            cond.append(m.AuditLog.entity == entity)
        if action:
            cond.append(m.AuditLog.action == action)
        total = await self.s.scalar(select(func.count()).select_from(m.AuditLog).where(*cond))
        rows = (
            await self.s.scalars(
                select(m.AuditLog)
                .where(*cond)
                .order_by(m.AuditLog.occurred_at.desc(), m.AuditLog.id)
                .limit(limit)
                .offset(offset)
            )
        ).all()
        return [
            {
                "id": str(r.id),
                "occurred_at": _iso(r.occurred_at),
                "action": r.action,
                "entity": r.entity,
                "entity_id": r.entity_id,
                "before": r.before,
                "after": r.after,
            }
            for r in rows
        ], int(total or 0)

    # --------------------------------------------------------------- settings

    async def _settings_row(self, user_id: UUID) -> m.UserSettings:
        row = await self.s.get(m.UserSettings, user_id)
        if row is None:  # Postgres creates it via trigger; SQLite/dev needs this
            row = m.UserSettings(user_id=user_id)
            self.s.add(row)
            await self.s.flush()
        return row

    @staticmethod
    def settings_dict(row: m.UserSettings) -> dict[str, Any]:
        out = {k: _jsonable(getattr(row, k)) for k in SETTINGS_FIELDS}
        for k in ("account_size", "base_risk_pct", "growth_risk_pct", "min_equity"):
            out[k] = float(out[k])
        out["disclaimer_accepted_at"] = _iso(row.disclaimer_accepted_at)
        return out

    async def get_settings(self, user_id: UUID) -> dict[str, Any]:
        row = await self._settings_row(user_id)
        await self.s.commit()
        return self.settings_dict(row)

    async def update_settings(self, user_id: UUID, changes: dict[str, Any]) -> dict[str, Any]:
        unknown = set(changes) - set(SETTINGS_FIELDS)
        if unknown:
            raise InvalidInput(f"unknown settings: {sorted(unknown)}")
        row = await self._settings_row(user_id)
        before = {k: _jsonable(getattr(row, k)) for k in changes}
        for key, value in changes.items():
            setattr(row, key, value)
        await self.s.flush()
        after = {k: _jsonable(getattr(row, k)) for k in changes}
        if before != after:
            self._audit(user_id, "settings.update", "settings", user_id, before, after)
        await self.s.commit()
        return self.settings_dict(row)

    async def accept_disclaimer(self, user_id: UUID) -> dict[str, Any]:
        row = await self._settings_row(user_id)
        if row.disclaimer_accepted_at is None:
            row.disclaimer_accepted_at = datetime.now(timezone.utc)
            self._audit(user_id, "disclaimer.accept", "settings", user_id, None, None)
        await self.s.commit()
        return self.settings_dict(row)

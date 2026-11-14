"""Repository behaviour: isolation, rules, audit trail, immutability, persistence."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import select

from app import database
from app import models as m
from app.repositories.sql import InvalidInput, Repo
from app.services.portfolio import Trade


@pytest.fixture
async def repo():
    async with database.get_session() as session:
        yield Repo(session)


async def _user(repo: Repo, email: str | None = None):
    uid = uuid4()
    await repo.ensure_user(uid, email or f"{uid}@example.com")
    return uid


def _trade(uid, pid, **overrides) -> Trade:
    base = dict(
        id=uuid4(),
        user_id=uid,
        portfolio_id=pid,
        symbol="AAPL",
        trade_type="put",
        direction="short",
        entry_price=2.0,
        exit_price=None,
        quantity=3,
        entry_date=date(2026, 1, 5),
        exit_date=None,
        strike=190.0,
        expiry=date(2026, 2, 20),
        strategy="Put Credit Spread",
        layer="base",
        band="A",
        risk_amount=1250.0,
        credit=1.1,
    )
    base.update(overrides)
    return Trade(**base)


# ---------------------------------------------------------------- users


async def test_ensure_user_is_idempotent_and_handles_email_clash(repo: Repo) -> None:
    uid = uuid4()
    await repo.ensure_user(uid, "same@example.com")
    await repo.ensure_user(uid, "same@example.com")  # no error, no duplicate
    other = uuid4()
    await repo.ensure_user(other, "same@example.com")  # email already used by another id
    rows = (await repo.s.scalars(select(m.User))).all()
    assert {r.id for r in rows} == {uid, other}


# ------------------------------------------------------------ portfolios


async def test_portfolio_rules_and_isolation(repo: Repo) -> None:
    a, b = await _user(repo), await _user(repo)
    pa = await repo.create_portfolio(a, "Main", "d")
    with pytest.raises(ValueError):
        await repo.create_portfolio(a, "Main")  # duplicate name for the same user
    await repo.create_portfolio(b, "Main")  # same name is fine for another user

    with pytest.raises(KeyError):
        await repo.get_portfolio(b, pa.id)  # other user's portfolio looks like "not found"

    renamed = await repo.update_portfolio(a, pa.id, name="Core")
    assert renamed.name == "Core"
    await repo.create_portfolio(a, "Second")
    with pytest.raises(ValueError):
        await repo.update_portfolio(a, pa.id, name="Second")


async def test_portfolio_with_trades_cannot_be_deleted(repo: Repo) -> None:
    uid = await _user(repo)
    p = await repo.create_portfolio(uid, "P")
    await repo.add_trade(_trade(uid, p.id))
    with pytest.raises(ValueError):
        await repo.delete_portfolio(uid, p.id)

    empty = await repo.create_portfolio(uid, "Empty")
    await repo.delete_portfolio(uid, empty.id)
    with pytest.raises(KeyError):
        await repo.get_portfolio(uid, empty.id)


# ---------------------------------------------------------------- trades


async def test_trade_roundtrip_keeps_strategy_fields(repo: Repo) -> None:
    uid = await _user(repo)
    p = await repo.create_portfolio(uid, "P")
    t = await repo.add_trade(_trade(uid, p.id))
    got = await repo.get_trade(uid, t.id)
    assert (got.strike, got.expiry, got.layer, got.band) == (190.0, date(2026, 2, 20), "base", "A")
    assert got.risk_amount == 1250.0 and got.credit == 1.1
    assert got.entry_date == date(2026, 1, 5)


async def test_trade_cannot_be_added_to_someone_elses_portfolio(repo: Repo) -> None:
    a, b = await _user(repo), await _user(repo)
    pa = await repo.create_portfolio(a, "P")
    with pytest.raises(KeyError):
        await repo.add_trade(_trade(b, pa.id))


async def test_list_trades_filters_sorting_and_pagination(repo: Repo) -> None:
    uid = await _user(repo)
    p = await repo.create_portfolio(uid, "P")
    for i, sym in enumerate(["AAPL", "MSFT", "TSLA", "NVDA", "AMD"]):
        await repo.add_trade(_trade(uid, p.id, symbol=sym, entry_date=date(2026, 1, 1 + i)))
    first = (await repo.list_trades(uid, symbol="AAPL"))[0][0]
    await repo.close_trade(uid, first.id, 3.0, date(2026, 1, 20))

    rows, total = await repo.list_trades(uid)
    assert total == 5 and rows[0].symbol == "AMD"  # newest entry first by default
    assert [t.symbol for t in (await repo.list_trades(uid, sort="symbol"))[0]][:2] == [
        "AAPL",
        "AMD",
    ]
    assert (await repo.list_trades(uid, status="closed"))[1] == 1
    assert (await repo.list_trades(uid, status="open"))[1] == 4

    page, total = await repo.list_trades(uid, sort="symbol", limit=2, offset=2)
    assert total == 5 and [t.symbol for t in page] == ["MSFT", "NVDA"]

    with pytest.raises(InvalidInput):
        await repo.list_trades(uid, sort="entry_price")  # not an allowed sort field


async def test_close_trade_rules(repo: Repo) -> None:
    uid, other = await _user(repo), await _user(repo)
    p = await repo.create_portfolio(uid, "P")
    t = await repo.add_trade(_trade(uid, p.id))

    with pytest.raises(KeyError):
        await repo.close_trade(other, t.id, 3.0, date(2026, 1, 9))
    with pytest.raises(InvalidInput):
        await repo.close_trade(uid, t.id, 3.0, date(2026, 1, 1))  # before entry date

    closed = await repo.close_trade(uid, t.id, 3.0, date(2026, 1, 9))
    assert closed.exit_price == 3.0 and closed.exit_date == date(2026, 1, 9)
    with pytest.raises(ValueError, match="already closed"):
        await repo.close_trade(uid, t.id, 4.0, date(2026, 1, 10))
    assert (await repo.get_trade(uid, t.id)).exit_price == 3.0  # the first close stands


# ------------------------------------------------------------------ audit


async def test_every_change_is_audited_with_before_and_after(repo: Repo) -> None:
    uid = await _user(repo)
    p = await repo.create_portfolio(uid, "P")
    t = await repo.add_trade(_trade(uid, p.id))
    await repo.close_trade(uid, t.id, 3.0, date(2026, 1, 9))
    await repo.update_trade_notes(uid, t.id, "rolled from last week")

    rows, total = await repo.list_audit(uid)
    actions = [r["action"] for r in rows]
    assert total == len(rows) == 4
    assert set(actions) == {"portfolio.create", "trade.add", "trade.close", "trade.notes"}

    close = next(r for r in rows if r["action"] == "trade.close")
    assert close["before"]["exit_price"] is None and close["after"]["exit_price"] == 3.0
    assert close["entity"] == "trade" and close["entity_id"] == str(t.id)

    only_trades, n = await repo.list_audit(uid, entity="trade")
    assert n == 3 and all(r["entity"] == "trade" for r in only_trades)


async def test_audit_log_is_per_user_and_date_filterable(repo: Repo) -> None:
    a, b = await _user(repo), await _user(repo)
    await repo.create_portfolio(a, "A")
    await repo.create_portfolio(b, "B")
    assert (await repo.list_audit(a))[1] == 1
    now = datetime.now(timezone.utc)
    assert (await repo.list_audit(a, start=now - timedelta(minutes=5)))[1] == 1
    assert (await repo.list_audit(a, end=now - timedelta(days=1)))[1] == 0


# ------------------------------------------------------------ immutability


async def test_log_rows_cannot_be_modified_or_deleted(repo: Repo) -> None:
    uid = await _user(repo)
    p = await repo.create_portfolio(uid, "P")  # creates an audit row
    await repo.log_signal(uid, kind="gate", decision="blocked", symbol="aapl", rule_id="BR-017")

    audit = (await repo.s.scalars(select(m.AuditLog))).first()
    signal = (await repo.s.scalars(select(m.SignalLog))).first()
    assert audit is not None and signal is not None and signal.symbol == "AAPL"

    audit.action = "tampered"
    with pytest.raises(m.ImmutableRecordError):
        await repo.s.commit()
    await repo.s.rollback()

    await repo.s.delete(signal)
    with pytest.raises(m.ImmutableRecordError):
        await repo.s.commit()
    await repo.s.rollback()

    # Still there, unchanged.
    assert (await repo.list_audit(uid))[0][0]["action"] == "portfolio.create"
    assert (await repo.list_signals(uid))[1] == 1
    assert p.id  # (portfolio itself is untouched)


async def test_signal_log_filters(repo: Repo) -> None:
    uid = await _user(repo)
    await repo.log_signal(uid, kind="gate", decision="blocked", symbol="AAPL", rule_id="BR-017")
    await repo.log_signal(uid, kind="gate", decision="blocked", symbol="TSLA", rule_id="BR-020")
    await repo.log_signal(uid, kind="gate", decision="allowed", symbol="AAPL")

    assert (await repo.list_signals(uid))[1] == 3
    assert (await repo.list_signals(uid, symbol="aapl"))[1] == 2
    assert (await repo.list_signals(uid, rule_id="BR-020"))[1] == 1
    assert (await repo.list_signals(uid, decision="allowed"))[1] == 1


# ------------------------------------------------------------- watchlists


async def test_watchlists(repo: Repo) -> None:
    a, b = await _user(repo), await _user(repo)
    wl = await repo.create_watchlist(a, "Core", ["aapl", "AAPL", " msft ", ""])
    assert wl["symbols"] == ["AAPL", "MSFT"]  # normalised and de-duplicated

    with pytest.raises(ValueError):
        await repo.create_watchlist(a, "Core")
    from uuid import UUID

    wid = UUID(wl["id"])
    with pytest.raises(KeyError):
        await repo.get_watchlist(b, wid)  # not b's

    after = await repo.add_symbol(a, wid, "nvda")
    assert after["symbols"] == ["AAPL", "MSFT", "NVDA"]
    assert (await repo.add_symbol(a, wid, "NVDA"))["symbols"] == after["symbols"]  # idempotent
    assert (await repo.remove_symbol(a, wid, "msft"))["symbols"] == ["AAPL", "NVDA"]
    with pytest.raises(KeyError):
        await repo.remove_symbol(a, wid, "ZZZZ")

    await repo.delete_watchlist(a, wid)
    assert await repo.list_watchlists(a) == []


async def test_symbol_flags(repo: Repo) -> None:
    uid = await _user(repo)
    assert await repo.get_symbol_flags(uid) == {}
    await repo.set_symbol_flag(uid, "tsla", True, "earnings rumour")
    await repo.set_symbol_flag(uid, "AAPL", False)
    flags = await repo.get_symbol_flags(uid)
    assert flags["TSLA"] == {"news_flag": True, "note": "earnings rumour"}
    await repo.set_symbol_flag(uid, "TSLA", False)
    assert (await repo.get_symbol_flags(uid, ["tsla"]))["TSLA"]["news_flag"] is False


# --------------------------------------------------------------- settings


async def test_settings_defaults_update_and_audit(repo: Repo) -> None:
    uid = await _user(repo)
    s = await repo.get_settings(uid)
    assert s["account_size"] == 100000 and s["enforce_gate"] is True
    assert s["band_caps"] == {"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}
    assert s["regime_weights"] == {"trend": 40, "vix": 30, "iv_rank": 30}
    assert s["disclaimer_accepted_at"] is None

    updated = await repo.update_settings(uid, {"account_size": 75000, "base_risk_pct": 1.0})
    assert updated["account_size"] == 75000 and updated["base_risk_pct"] == 1.0

    rows, _ = await repo.list_audit(uid, action="settings.update")
    assert rows[0]["before"]["account_size"] == 100000 and rows[0]["after"]["account_size"] == 75000

    with pytest.raises(InvalidInput):
        await repo.update_settings(uid, {"not_a_setting": 1})


async def test_disclaimer_is_recorded_once(repo: Repo) -> None:
    uid = await _user(repo)
    first = (await repo.accept_disclaimer(uid))["disclaimer_accepted_at"]
    again = (await repo.accept_disclaimer(uid))["disclaimer_accepted_at"]
    assert first is not None and first == again
    assert (await repo.list_audit(uid, action="disclaimer.accept"))[1] == 1


# ------------------------------------------------------------ persistence


async def test_data_survives_a_new_session() -> None:
    """The 'restart' check: a brand-new session (like a new request/process) sees the data."""
    uid = uuid4()
    async with database.get_session() as s1:
        r1 = Repo(s1)
        await r1.ensure_user(uid, "p@example.com")
        p = await r1.create_portfolio(uid, "Durable")
        await r1.add_trade(_trade(uid, p.id))

    async with database.get_session() as s2:
        r2 = Repo(s2)
        portfolios = await r2.list_portfolios(uid)
        assert [x.name for x in portfolios] == ["Durable"]
        assert len(portfolios[0].trades) == 1

"""Smoke-test the persistence layer against a REAL PostgreSQL database.

Unit tests run on SQLite. This script checks what SQLite cannot: that migration 007 was
applied correctly and that the Postgres triggers really make the log tables append-only.

SAFETY: it writes rows and runs ``TRUNCATE`` on the log tables to prove they are protected.
Run it ONLY against a throwaway/dev database (for example a separate free Supabase project).

    SMOKE_DB_URL=postgresql://... uv run python scripts/smoke_db.py --disposable

It refuses to run without both the ``SMOKE_DB_URL`` variable and the ``--disposable`` flag, and
without a URL it never reads ``DATABASE_URL``.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from app import database  # noqa: E402
from app.repositories.sql import Repo  # noqa: E402
from app.services.portfolio import Trade  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))


async def expect_rejected(session, sql: str, params: dict | None = None) -> tuple[bool, str]:
    """True if the database refused the statement (the trigger fired)."""
    try:
        await session.execute(text(sql), params or {})
        await session.commit()
        return False, "statement succeeded (log is NOT append-only)"
    except Exception as exc:  # noqa: BLE001
        await session.rollback()
        return True, str(exc).splitlines()[0]


async def run() -> None:
    uid = uuid4()
    async with database.get_session() as s:
        repo = Repo(s)

        print("Schema")
        tables = {
            r[0]
            for r in (
                await s.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
                    )
                )
            ).all()
        }
        needed = {
            "users",
            "portfolios",
            "trades",
            "user_settings",
            "watchlists",
            "watchlist_items",
            "symbol_flags",
            "signal_log",
            "audit_events",
        }
        check("migration 007 tables exist", needed <= tables, f"missing: {sorted(needed - tables)}")
        cols = {
            r[0]
            for r in (
                await s.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns WHERE table_name='trades'"
                    )
                )
            ).all()
        }
        check(
            "trades has strategy columns",
            {"strike", "expiry", "layer", "band", "risk_amount"} <= cols,
        )

        print("Persistence")
        await repo.ensure_user(uid, f"smoke+{uid}@example.invalid")
        portfolio = await repo.create_portfolio(uid, "Smoke")
        trade = await repo.add_trade(
            Trade(
                id=uuid4(),
                user_id=uid,
                portfolio_id=portfolio.id,
                symbol="SMOKE",
                trade_type="put",
                direction="short",
                entry_price=2.0,
                exit_price=None,
                quantity=1,
                entry_date=date(2026, 1, 5),
                exit_date=None,
                strike=100.0,
                expiry=date(2026, 2, 20),
                strategy="Put Credit Spread",
                layer="base",
                band="A",
                risk_amount=500.0,
                credit=1.0,
            )
        )
        closed = await repo.close_trade(uid, trade.id, 1.5, date(2026, 1, 9))
        check("trade add + close round-trips", closed.exit_price == 1.5 and closed.strike == 100.0)
        settings = await repo.get_settings(uid)
        check("user_settings row has defaults", settings["account_size"] == 100000)
        await repo.log_signal(
            uid, kind="smoke", decision="info", symbol="SMOKE", message="smoke test"
        )
        audit, total = await repo.list_audit(uid)
        check("audit rows written with the change", total >= 3, f"found {total}")

        print("Append-only logs (Postgres triggers)")
        for table in ("audit_events", "signal_log"):
            ok, why = await expect_rejected(
                s, f"UPDATE {table} SET user_id = user_id WHERE user_id = :u", {"u": uid}
            )
            check(f"UPDATE on {table} is rejected", ok, why)
            ok, why = await expect_rejected(
                s, f"DELETE FROM {table} WHERE user_id = :u", {"u": uid}
            )
            check(f"DELETE on {table} is rejected", ok, why)
            ok, why = await expect_rejected(s, f"TRUNCATE {table}")
            check(f"TRUNCATE on {table} is rejected", ok, why)

        print("Cleanup (log rows cannot be deleted by design and are left behind)")
        for table in ("trades", "portfolios", "symbol_flags", "user_settings"):
            await s.execute(text(f"DELETE FROM {table} WHERE user_id = :u"), {"u": uid})
        await s.execute(text("DELETE FROM users WHERE id = :u"), {"u": uid})
        await s.commit()


async def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--disposable", action="store_true", help="confirm the database can be written to"
    )
    args = parser.parse_args()

    url = os.environ.get("SMOKE_DB_URL")
    if not url or not args.disposable:
        print(
            "Refusing to run: set SMOKE_DB_URL to a THROWAWAY database and pass --disposable.",
            file=sys.stderr,
        )
        return 2
    if url == os.environ.get("DATABASE_URL"):
        print(
            "Refusing to run: SMOKE_DB_URL equals DATABASE_URL (your real database).",
            file=sys.stderr,
        )
        return 2

    database.configure_engine(url)
    try:
        await run()
    finally:
        if database.engine is not None:
            await database.engine.dispose()

    failed = [name for name, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

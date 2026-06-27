"""
Round-trip SQL parser test: ensure every .sql file in
database/migrations/ parses cleanly using ``pglast`` (or a regex fallback
when pglast is unavailable).

This guards against committing SQL with syntax errors that would only
surface at deploy time.

Run with:  uv run pytest backend/tests/test_db_sql.py -v
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "database" / "migrations"


def _discover_sql_files() -> list[Path]:
    return sorted(
        p
        for p in MIGRATIONS_DIR.glob("*.sql")
        if p.is_file()
    )


@pytest.mark.parametrize("sql_path", _discover_sql_files(), ids=lambda p: p.name)
def test_sql_parses(sql_path: Path) -> None:
    sql = sql_path.read_text(encoding="utf-8")
    try:
        import pglast  # type: ignore
        pglast.parse_sql(sql)
    except ImportError:
        # Fallback: at minimum, ensure files are non-empty and contain a
        # BEGIN/COMMIT wrapper or a CREATE/INSERT statement.
        assert sql.strip(), f"{sql_path.name} is empty"
        upper = sql.upper()
        assert (
            ("CREATE" in upper)
            or ("INSERT" in upper)
            or ("DROP" in upper)
        ), f"{sql_path.name} contains no DDL/DML"
    except Exception as exc:  # pragma: no cover - pglast raises on bad SQL
        pytest.fail(f"{sql_path.name} failed to parse: {exc}")


def test_migration_ordering_is_monotonic() -> None:
    """Migration filenames must sort in apply order."""
    files = _discover_sql_files()
    prefixes = [re.match(r"^(\d{3,})_", f.name).group(1) for f in files]  # type: ignore[union-attr]
    assert prefixes == sorted(prefixes), (
        f"Migration files are not in numeric order: {prefixes}"
    )


def test_every_migration_has_a_down_or_is_reversible() -> None:
    """Every _up migration should either have a *_down.sql counterpart
    or be idempotent (CREATE ... IF NOT EXISTS, etc.)."""
    ups = [p for p in _discover_sql_files() if "_down" not in p.name]
    for up in ups:
        down = up.with_name(up.name.replace(".sql", "_down.sql"))
        if down.exists():
            continue
        sql = up.read_text(encoding="utf-8").upper()
        # If it's not a down-able migration, it must be idempotent.
        if "CREATE" in sql and "IF NOT EXISTS" in sql:
            continue
        # Bootstrap migrations (001, 002) typically have a corresponding down.
        pytest.fail(
            f"{up.name} has no _down.sql and is not idempotent (missing IF NOT EXISTS)."
        )

"""Pytest fixtures shared across backend tests."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Make the `app` package importable when running `pytest` from repo root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dataclasses import dataclass, field, replace  # noqa: E402
from datetime import date, timedelta  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402

import app.models  # noqa: E402,F401  (registers every model on Base.metadata)
from app import database  # noqa: E402
from app.domain import regime_score as rs  # noqa: E402
from app.domain.alerts import MarketInput  # noqa: E402
from app.domain.gate import SymbolData  # noqa: E402
from app.main import app  # noqa: E402
from app.services import regime_service  # noqa: E402
from app.services.position_data import get_position_data_provider  # noqa: E402
from app.services.sector_data import get_sector_provider  # noqa: E402
from app.services.symbol_data import get_symbol_data_provider  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """A FastAPI test client. Override `get_current_user` per-test for auth."""
    return TestClient(app)


@pytest.fixture
def dev_headers() -> dict[str, str]:
    """Headers that the dev-token fallback accepts (no Supabase required)."""
    return {"Authorization": "Bearer dev:test-user"}


@pytest.fixture(autouse=True)
def _dev_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests use dev tokens, which only work when ENVIRONMENT=development."""
    from app.config import settings

    monkeypatch.setattr(settings, "ENVIRONMENT", "development")


def _postgres_test_url() -> str | None:
    """Opt-in: run the suite against a THROWAWAY PostgreSQL built from ``database/migrations``.

    ``TEST_PG_URL=postgresql://... uv run pytest tests -q``. Every table is emptied before each
    test, so never point this at a database you care about; it refuses your ``DATABASE_URL``.
    """
    url = os.environ.get("TEST_PG_URL")
    if not url:
        return None
    from app.config import settings

    if settings.DATABASE_URL and database.normalize_url(url) == database.normalize_url(
        settings.DATABASE_URL
    ):
        pytest.exit("TEST_PG_URL equals DATABASE_URL (your real database): refusing to run.")
    return url


def _empty_postgres(url: str) -> None:
    # session_replication_role=replica switches off the append-only triggers for this cleanup only.
    sync_engine = create_engine(database.normalize_url(url).replace("+asyncpg", "+psycopg"))
    with sync_engine.begin() as conn:
        tables = conn.execute(
            text("select tablename from pg_tables where schemaname = 'public'")
        ).scalars()
        names = ", ".join(f'"{t}"' for t in tables if t != "health_check")
        conn.execute(text("set session_replication_role = replica"))
        conn.execute(text(f"truncate table {names} restart identity cascade"))
    sync_engine.dispose()


@pytest.fixture(autouse=True)
def _fresh_database(tmp_path: Path):
    """Every test gets its own empty database: a temp SQLite file (no cross-test leakage, and no
    event-loop sharing between the fixture and the TestClient), or an emptied PostgreSQL when
    ``TEST_PG_URL`` is set."""
    pg_url = _postgres_test_url()
    if pg_url:
        _empty_postgres(pg_url)
        database.configure_engine(pg_url)
    else:
        db_file = tmp_path / "test.db"
        database.sanitize_for_sqlite(database.Base.metadata)
        sync_engine = create_engine(f"sqlite:///{db_file}")
        database.Base.metadata.create_all(sync_engine)
        sync_engine.dispose()
        database.configure_engine(f"sqlite+aiosqlite:///{db_file}")
    yield
    if database.engine is not None:
        asyncio.run(database.engine.dispose())


# --------------------------------------------------------------------------- market-data fakes
# Tests never touch the network: regime inputs and symbol data are supplied by these fakes.
# Defaults describe a calm, rising market and a liquid, large, no-news stock.


@dataclass
class RegimeInputs:
    spy: list[float] | None = field(default_factory=lambda: [100 + i * 0.5 for i in range(250)])
    vix: list[float] | None = field(default_factory=lambda: [15.0] * 250)

    def falling_market(self) -> None:
        self.spy = [200 - i * 0.5 for i in range(250)]
        self.vix = [20.0] * 200 + [20 + i for i in range(50)]

    def unavailable(self) -> None:
        self.spy = self.vix = None


@pytest.fixture(autouse=True)
def regime_inputs(monkeypatch: pytest.MonkeyPatch) -> RegimeInputs:
    inputs = RegimeInputs()
    monkeypatch.setattr(rs, "fetch_inputs", lambda: (inputs.spy, inputs.vix))
    regime_service.clear_cache()
    yield inputs
    regime_service.clear_cache()


class FakeSymbolData:
    """Stands in for the yfinance lookup; edit ``.data`` per test, inspect ``.calls``."""

    def __init__(self) -> None:
        self.data = SymbolData(
            symbol="",
            fetched=True,
            quote_type="EQUITY",
            market_cap=500e9,
            next_earnings=date.today() + timedelta(days=45),
            spread_pct=2.0,
            open_interest=5000,
        )
        self.calls: list[tuple[str, dict]] = []

    def __call__(self, symbol: str, **kwargs) -> SymbolData:
        self.calls.append((symbol, kwargs))
        return replace(self.data, symbol=symbol)


@pytest.fixture(autouse=True)
def symbol_data():
    fake = FakeSymbolData()
    app.dependency_overrides[get_symbol_data_provider] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_symbol_data_provider, None)


class FakePositionData:
    """Stands in for live position prices. Default: calm, out of the money, plenty of time.

    Set ``by_symbol[symbol]`` to a ``MarketInput`` to give one symbol different data, or set
    ``unavailable = True`` to simulate a failed price feed.
    """

    def __init__(self) -> None:
        self.by_symbol: dict[str, MarketInput] = {}
        self.unavailable = False
        self.calls: list[str] = []

    def __call__(self, symbol: str, *, trade_type: str, strike=None, expiry=None) -> MarketInput:
        self.calls.append(symbol)
        if self.unavailable:
            return MarketInput(available=False)
        if symbol in self.by_symbol:
            return self.by_symbol[symbol]
        if trade_type == "stock":
            return MarketInput(available=True, spot=100.0, mark=100.0)
        # A put/call far from the money: spot 100 vs the strike, mark close to the entry price.
        return MarketInput(
            available=True,
            spot=200.0 if trade_type == "put" else 50.0,
            mark=1.9,
            delta=-0.15 if trade_type == "put" else 0.15,
            theta=0.04,
        )


class FakeSectors:
    """Stands in for the sector lookup. Unknown symbols return None."""

    def __init__(self) -> None:
        self.by_symbol: dict[str, str | None] = {
            "AAPL": "Technology",
            "MSFT": "Technology",
            "XOM": "Energy",
        }

    def __call__(self, symbol: str) -> str | None:
        return self.by_symbol.get(symbol)


@pytest.fixture(autouse=True)
def sectors():
    fake = FakeSectors()
    app.dependency_overrides[get_sector_provider] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_sector_provider, None)


@pytest.fixture(autouse=True)
def position_data():
    fake = FakePositionData()
    app.dependency_overrides[get_position_data_provider] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_position_data_provider, None)

"""Pytest fixtures shared across backend tests."""

from __future__ import annotations

import asyncio
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
from sqlalchemy import create_engine  # noqa: E402

import app.models  # noqa: E402,F401  (registers every model on Base.metadata)
from app import database  # noqa: E402
from app.domain import regime_score as rs  # noqa: E402
from app.domain.gate import SymbolData  # noqa: E402
from app.main import app  # noqa: E402
from app.services import regime_service  # noqa: E402
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


@pytest.fixture(autouse=True)
def _fresh_database(tmp_path: Path):
    """Every test gets its own empty SQLite database (a temp file: no cross-test leakage,
    and no event-loop sharing between the fixture and the TestClient)."""
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

"""Pytest fixtures shared across backend tests."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make the `app` package importable when running `pytest` from repo root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402

import app.models  # noqa: E402,F401  (registers every model on Base.metadata)
from app import database  # noqa: E402
from app.main import app  # noqa: E402


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

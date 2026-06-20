"""Pytest fixtures shared across backend tests."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the `app` package importable when running `pytest` from repo root.
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import reset_store


@pytest.fixture
def client() -> TestClient:
    """A FastAPI test client. Override `get_current_user` per-test for auth."""
    return TestClient(app)


@pytest.fixture
def dev_headers() -> dict[str, str]:
    """Headers that the dev-token fallback accepts (no Supabase required)."""
    return {"Authorization": "Bearer dev:test-user"}


@pytest.fixture(autouse=True)
def _reset_in_memory_store():
    """Ensure each test starts with a fresh in-memory portfolio store."""
    reset_store()
    yield
    reset_store()

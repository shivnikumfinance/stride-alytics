"""End-to-end API tests for the FastAPI v1 surface.

These tests use the dev-token auth path (no Supabase required) and
validate the request/response contract of every Blueprint endpoint.

Run with:  uv run pytest backend/tests/test_api.py -v
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["name"] == "StrideAlytics"


def test_unauthenticated_greeks_rejected(client: TestClient) -> None:
    r = client.post(
        "/api/v1/greeks/calculate",
        json={
            "spot": 100,
            "strike": 100,
            "time_to_expiry": 0.1,
            "option_type": "call",
        },
    )
    assert r.status_code == 401


def test_greeks_calculate(client: TestClient, dev_headers) -> None:
    r = client.post(
        "/api/v1/greeks/calculate",
        headers=dev_headers,
        json={
            "spot": 100,
            "strike": 100,
            "time_to_expiry": 0.0822,
            "volatility": 0.3,
            "option_type": "call",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "delta" in body and "gamma" in body
    assert body["delta"] > 0  # long call has positive delta


def test_greeks_invalid_inputs(client: TestClient, dev_headers) -> None:
    r = client.post(
        "/api/v1/greeks/calculate",
        headers=dev_headers,
        json={"spot": -1, "strike": 100, "time_to_expiry": 0.1, "option_type": "call"},
    )
    assert r.status_code == 422


def test_screener_limits(client: TestClient, dev_headers) -> None:
    r = client.get("/api/v1/screener/limits", headers=dev_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["plan"] in ("free", "pro")
    assert body["data"]["max_results_per_call"] >= 1


def test_screener_run(client: TestClient, dev_headers) -> None:
    r = client.post(
        "/api/v1/screener/run",
        headers=dev_headers,
        json={
            "symbol": "AAPL",
            "expiry_days_min": 0,
            "expiry_days_max": 60,
            "min_volume": 0,
            "min_open_interest": 0,
            "limit": 5,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["symbol"] == "AAPL"
    assert body["count"] <= 5


def test_screener_free_tier_402(client: TestClient, dev_headers) -> None:
    """A free user requesting >50 results should be rejected."""
    r = client.post(
        "/api/v1/screener/run",
        headers=dev_headers,
        json={
            "symbol": "AAPL",
            "expiry_days_min": 0,
            "expiry_days_max": 60,
            "min_volume": 0,
            "min_open_interest": 0,
            "limit": 100,
        },
    )
    assert r.status_code == 402
    assert "Free tier" in r.json()["error"]["message"]


def test_regime_detect(client: TestClient, dev_headers) -> None:
    r = client.get("/api/v1/regime/SPY", headers=dev_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["symbol"] == "SPY"
    assert body["regime"] in ("bull", "bear", "ranging")


def test_auth_me(client: TestClient, dev_headers) -> None:
    r = client.get("/api/v1/auth/me", headers=dev_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["user_id"] == "test-user"
    assert body["data"]["subscription_plan"] == "free"


def test_portfolio_create_and_summary(client: TestClient, dev_headers) -> None:
    # Create
    r = client.post(
        "/api/v1/portfolio",
        headers=dev_headers,
        json={"name": "API Test", "description": "Created by pytest"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total_trades"] == 0

    # List
    r = client.get("/api/v1/portfolio", headers=dev_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert any(p["name"] == "API Test" for p in data)

"""End-to-end API tests for the FastAPI v1 surface.

These tests use the dev-token auth path (no Supabase required) and
validate the request/response contract of every Blueprint endpoint.

Run with:  uv run pytest backend/tests/test_api.py -v
"""

from __future__ import annotations

import pytest
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


def test_screener_large_limit_allowed(client: TestClient, dev_headers) -> None:
    """There are no plan tiers, so a limit above 50 is accepted."""
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
    assert r.status_code == 200, r.text


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
    assert "subscription_plan" not in body["data"]


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


def test_health_endpoints_need_no_auth(client: TestClient) -> None:
    for path in ("/health", "/api/v1/health"):
        r = client.get(path)
        assert r.status_code == 200, path


# --- Dev-token gating -------------------------------------------------------


@pytest.mark.parametrize("token", ["dev-admin-token", "dev:someone"])
def test_dev_tokens_rejected_outside_development(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, token: str
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", None)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_dev_admin_token_works_in_development(client: TestClient) -> None:
    r = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer dev-admin-token"})
    assert r.status_code == 200


def test_login_without_supabase_is_503_outside_development(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "SUPABASE_URL", None)
    r = client.post(
        "/api/v1/auth/login", json={"email": "a@example.com", "password": "password123"}
    )
    assert r.status_code == 503


# --- Supabase JWT verification ----------------------------------------------


def _supabase_token(secret: str, **claims) -> str:
    import time

    from jose import jwt

    payload = {"sub": "user-1", "email": "me@example.com", "aud": "authenticated"}
    payload["exp"] = int(time.time()) + 3600
    payload.update(claims)
    return jwt.encode(
        {k: v for k, v in payload.items() if v is not None}, secret, algorithm="HS256"
    )


@pytest.fixture
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> str:
    from app.config import settings

    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", "unit-test-secret")
    return "unit-test-secret"


def test_real_supabase_token_is_accepted(client: TestClient, jwt_secret: str) -> None:
    token = _supabase_token(jwt_secret)
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    assert r.json()["data"]["user_id"] == "user-1"


def test_token_with_wrong_audience_is_rejected(client: TestClient, jwt_secret: str) -> None:
    token = _supabase_token(jwt_secret, aud="something-else")
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_expired_and_badly_signed_tokens_are_rejected(client: TestClient, jwt_secret: str) -> None:
    expired = _supabase_token(jwt_secret, exp=1)
    forged = _supabase_token("some-other-secret")
    for token in (expired, forged):
        r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 401


# --- Trades -----------------------------------------------------------------


def _make_portfolio(client: TestClient, headers: dict[str, str]) -> str:
    r = client.post("/api/v1/portfolio", headers=headers, json={"name": "T"})
    assert r.status_code == 201, r.text
    return r.json()["portfolio_id"]


def _add_trade(client: TestClient, headers: dict[str, str], pid: str, symbol: str) -> dict:
    r = client.post(
        "/api/v1/trades",
        headers=headers,
        json={
            "portfolio_id": pid,
            "symbol": symbol,
            "trade_type": "call",
            "direction": "long",
            "entry_price": 2.0,
            "quantity": 1,
            "entry_date": "2026-01-02",
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_trades_get_unique_ids_and_close_targets_the_right_one(
    client: TestClient, dev_headers
) -> None:
    pid = _make_portfolio(client, dev_headers)
    first = _add_trade(client, dev_headers, pid, "AAPL")
    second = _add_trade(client, dev_headers, pid, "MSFT")
    assert first["trade_id"] != second["trade_id"]

    r = client.post(
        f"/api/v1/trades/{second['trade_id']}/close",
        headers=dev_headers,
        json={"exit_price": 3.0, "exit_date": "2026-01-10"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["symbol"] == "MSFT"

    trades = {
        t["symbol"]: t for t in client.get(f"/api/v1/trades/{pid}", headers=dev_headers).json()
    }
    assert trades["MSFT"]["open"] is False
    assert trades["AAPL"]["open"] is True


# ----------------------------------------------------------------- auth hardening


def test_refresh_token_is_read_from_the_body_not_the_url(client: TestClient) -> None:
    # Without Supabase configured the endpoint is not implemented, but the request shape is checked.
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": "abc"}).status_code in (
        501,
        502,
    )
    assert client.post("/api/v1/auth/refresh", params={"refresh_token": "abc"}).status_code == 422
    assert client.post("/api/v1/auth/refresh", json={}).status_code == 422
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": ""}).status_code == 422


def test_cors_never_combines_a_wildcard_with_credentials(client: TestClient) -> None:
    from app.config import settings

    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] or ["*"]
    origin = "https://example.com" if "*" in origins else origins[0]
    r = client.get("/health", headers={"Origin": origin})
    allowed = r.headers.get("access-control-allow-origin")
    credentials = r.headers.get("access-control-allow-credentials")
    if "*" in origins:
        assert allowed == "*" and credentials is None  # a browser would reject "*" + credentials
    else:
        assert allowed == origin and credentials == "true"
        other = client.get("/health", headers={"Origin": "https://evil.example"})
        assert other.headers.get("access-control-allow-origin") is None  # unlisted origins refused

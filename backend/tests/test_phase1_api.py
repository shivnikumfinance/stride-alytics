"""Phase 1 HTTP behaviour: portfolios, trades, watchlists, settings, logs."""

from __future__ import annotations

from fastapi.testclient import TestClient

ALICE = {"Authorization": "Bearer dev:alice"}
BOB = {"Authorization": "Bearer dev:bob"}


def _portfolio(client: TestClient, headers=ALICE, name: str = "P") -> str:
    r = client.post("/api/v1/portfolio", headers=headers, json={"name": name})
    assert r.status_code == 201, r.text
    return r.json()["portfolio_id"]


def _trade(client: TestClient, pid: str, headers=ALICE, **over) -> dict:
    body = {
        "portfolio_id": pid,
        "symbol": "AAPL",
        "trade_type": "put",
        "direction": "short",
        "entry_price": 2.0,
        "quantity": 1,
        "entry_date": "2026-01-05",
    }
    body.update(over)
    r = client.post("/api/v1/trades", headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


# ------------------------------------------------------------- portfolios


def test_portfolio_patch_delete_and_isolation(client: TestClient) -> None:
    pid = _portfolio(client, name="Main")
    assert (
        client.patch(f"/api/v1/portfolio/{pid}", headers=ALICE, json={"name": "Core"}).json()[
            "name"
        ]
        == "Core"
    )

    # Bob can neither see, change nor delete Alice's portfolio.
    assert client.get(f"/api/v1/portfolio/{pid}", headers=BOB).status_code == 404
    assert (
        client.patch(f"/api/v1/portfolio/{pid}", headers=BOB, json={"name": "x"}).status_code == 404
    )
    assert client.delete(f"/api/v1/portfolio/{pid}", headers=BOB).status_code == 404

    _trade(client, pid)
    assert client.delete(f"/api/v1/portfolio/{pid}", headers=ALICE).status_code == 409  # has trades
    empty = _portfolio(client, name="Empty")
    assert client.delete(f"/api/v1/portfolio/{empty}", headers=ALICE).status_code == 204
    assert client.get(f"/api/v1/portfolio/{empty}", headers=ALICE).status_code == 404


def test_duplicate_portfolio_name_is_409(client: TestClient) -> None:
    _portfolio(client, name="Dup")
    r = client.post("/api/v1/portfolio", headers=ALICE, json={"name": "Dup"})
    assert r.status_code == 409


# ---------------------------------------------------------------- trades


def test_trade_strategy_fields_roundtrip_and_validation(client: TestClient) -> None:
    pid = _portfolio(client)
    t = _trade(
        client,
        pid,
        strike=190,
        expiry="2026-02-20",
        strategy="Put Credit Spread",
        layer="base",
        band="B",
        risk_amount=1250,
        credit=1.1,
    )
    assert (t["strike"], t["expiry"], t["layer"], t["band"]) == (190, "2026-02-20", "base", "B")

    bad = client.post(
        "/api/v1/trades",
        headers=ALICE,
        json={
            "portfolio_id": pid,
            "symbol": "AAPL",
            "trade_type": "put",
            "direction": "short",
            "entry_price": 2,
            "quantity": 1,
            "entry_date": "2026-01-05",
            "band": "Z",
        },
    )
    assert bad.status_code == 422


def test_trade_list_pagination_filters_and_sort(client: TestClient) -> None:
    pid = _portfolio(client)
    for i, sym in enumerate(["AAPL", "MSFT", "TSLA", "NVDA"]):
        _trade(client, pid, symbol=sym, entry_date=f"2026-01-0{i + 1}")
    first = client.get("/api/v1/trades?symbol=aapl", headers=ALICE).json()["data"][0]
    client.post(
        f"/api/v1/trades/{first['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 3, "exit_date": "2026-01-20"},
    )

    page = client.get("/api/v1/trades?sort=symbol&limit=2&offset=1", headers=ALICE).json()
    assert page["total"] == 4 and page["limit"] == 2 and page["offset"] == 1
    assert [t["symbol"] for t in page["data"]] == ["MSFT", "NVDA"]
    assert client.get("/api/v1/trades?status=closed", headers=ALICE).json()["total"] == 1
    assert client.get("/api/v1/trades?status=open", headers=ALICE).json()["total"] == 3
    assert client.get("/api/v1/trades?sort=entry_price", headers=ALICE).status_code == 422
    assert client.get("/api/v1/trades?limit=0", headers=ALICE).status_code == 422
    assert client.get("/api/v1/trades", headers=BOB).json()["total"] == 0  # isolation


def test_close_rules_over_http(client: TestClient) -> None:
    pid = _portfolio(client)
    t = _trade(client, pid)
    url = f"/api/v1/trades/{t['trade_id']}/close"

    assert (
        client.post(url, headers=BOB, json={"exit_price": 3, "exit_date": "2026-01-09"}).status_code
        == 404
    )
    assert (
        client.post(
            url, headers=ALICE, json={"exit_price": 3, "exit_date": "2026-01-01"}
        ).status_code
        == 422
    )
    ok = client.post(url, headers=ALICE, json={"exit_price": 3, "exit_date": "2026-01-09"})
    assert ok.status_code == 200 and ok.json()["open"] is False and ok.json()["pnl"] == -1.0
    again = client.post(url, headers=ALICE, json={"exit_price": 9, "exit_date": "2026-01-10"})
    assert again.status_code == 409  # cannot be re-closed at a different price
    assert client.get(f"/api/v1/trades/{pid}", headers=ALICE).json()[0]["exit_price"] == 3


def test_notes_can_change_but_prices_cannot(client: TestClient) -> None:
    pid = _portfolio(client)
    t = _trade(client, pid)
    r = client.patch(f"/api/v1/trades/{t['trade_id']}", headers=ALICE, json={"notes": "rolled"})
    assert r.status_code == 200 and r.json()["notes"] == "rolled" and r.json()["entry_price"] == 2.0
    # extra fields are ignored; there is no way to edit prices through this endpoint
    r = client.patch(
        f"/api/v1/trades/{t['trade_id']}", headers=ALICE, json={"notes": "x", "entry_price": 99}
    )
    assert r.json()["entry_price"] == 2.0


def test_trades_survive_listing_across_requests(client: TestClient) -> None:
    pid = _portfolio(client)
    _trade(client, pid, symbol="MSFT")
    rows = client.get(f"/api/v1/trades/{pid}", headers=ALICE).json()
    assert [r["symbol"] for r in rows] == ["MSFT"]


def test_csv_export_is_scoped_and_neutralises_formulas(client: TestClient) -> None:
    pid = _portfolio(client)
    _trade(client, pid, symbol="AAPL", notes='=HYPERLINK("http://evil")')
    _trade(client, _portfolio(client, BOB, "B"), BOB, symbol="MSFT")

    r = client.get("/api/v1/trades/export.csv", headers=ALICE)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    lines = r.text.strip().splitlines()
    assert lines[0].startswith("trade_id,portfolio_id,symbol")
    assert len(lines) == 2 and "AAPL" in lines[1] and "MSFT" not in r.text
    assert "'=HYPERLINK" in r.text  # a leading quote stops it running as a formula


# ------------------------------------------------------------ watchlists


def test_watchlist_crud_export_and_isolation(client: TestClient) -> None:
    r = client.post(
        "/api/v1/watchlists", headers=ALICE, json={"name": "Core", "symbols": ["aapl", "msft"]}
    )
    assert r.status_code == 201
    wid = r.json()["data"]["id"]
    assert r.json()["data"]["symbols"] == ["AAPL", "MSFT"]
    assert (
        client.post("/api/v1/watchlists", headers=ALICE, json={"name": "Core"}).status_code == 409
    )

    assert client.get(f"/api/v1/watchlists/{wid}", headers=BOB).status_code == 404
    added = client.post(f"/api/v1/watchlists/{wid}/symbols", headers=ALICE, json={"symbol": "nvda"})
    assert added.json()["data"]["symbols"] == ["AAPL", "MSFT", "NVDA"]
    removed = client.delete(f"/api/v1/watchlists/{wid}/symbols/msft", headers=ALICE)
    assert removed.json()["data"]["symbols"] == ["AAPL", "NVDA"]
    assert client.delete(f"/api/v1/watchlists/{wid}/symbols/ZZZ", headers=ALICE).status_code == 404

    csv = client.get(f"/api/v1/watchlists/{wid}/export.csv", headers=ALICE).text.splitlines()
    assert csv[0] == "symbol,news_flag" and len(csv) == 3

    assert client.delete(f"/api/v1/watchlists/{wid}", headers=ALICE).status_code == 204
    assert client.get("/api/v1/watchlists", headers=ALICE).json()["data"] == []


# -------------------------------------------------------------- settings


def test_settings_defaults_update_and_validation(client: TestClient) -> None:
    s = client.get("/api/v1/settings", headers=ALICE).json()["data"]
    assert s["account_size"] == 100000 and s["enforce_gate"] is True
    assert s["band_caps"] == {"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}

    r = client.put(
        "/api/v1/settings",
        headers=ALICE,
        json={"account_size": 50000, "base_risk_pct": 1.0, "theme": "dark"},
    )
    assert r.status_code == 200 and r.json()["data"]["account_size"] == 50000
    # Partial update leaves other fields alone; Bob is unaffected.
    assert r.json()["data"]["growth_risk_pct"] == 2.5
    assert client.get("/api/v1/settings", headers=BOB).json()["data"]["account_size"] == 100000


def test_settings_reject_bad_values(client: TestClient) -> None:
    bad_bodies = [
        {"band_caps": {"A": 30, "B": 25}},  # missing bands
        {"band_caps": {"A": 130, "B": 25, "C": 20, "D": 15, "E": 10}},  # over 100%
        {"regime_weights": {"trend": 0, "vix": 0, "iv_rank": 0}},  # all zero
        {"regime_weights": {"trend": 50, "vix": 50}},  # missing key
        {"base_risk_pct": 0},
        {"base_risk_pct": 50},
        {"account_size": -1},
        {"theme": "neon"},
    ]
    for body in bad_bodies:
        r = client.put("/api/v1/settings", headers=ALICE, json=body)
        assert r.status_code == 422, body


def test_disclaimer_acceptance(client: TestClient) -> None:
    assert (
        client.get("/api/v1/settings", headers=ALICE).json()["data"]["disclaimer_accepted_at"]
        is None
    )
    r = client.post("/api/v1/settings/disclaimer", headers=ALICE)
    assert r.json()["data"]["disclaimer_accepted_at"] is not None
    assert (
        client.get("/api/v1/settings", headers=BOB).json()["data"]["disclaimer_accepted_at"] is None
    )


# ------------------------------------------------------------------ logs


def test_changes_appear_in_the_audit_log_and_logs_are_read_only(client: TestClient) -> None:
    pid = _portfolio(client)
    t = _trade(client, pid)
    client.post(
        f"/api/v1/trades/{t['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 3, "exit_date": "2026-01-09"},
    )
    client.put("/api/v1/settings", headers=ALICE, json={"account_size": 60000})

    audit = client.get("/api/v1/logs/audit", headers=ALICE).json()
    actions = {r["action"] for r in audit["data"]}
    assert {"portfolio.create", "trade.add", "trade.close", "settings.update"} <= actions
    assert audit["total"] == len(audit["data"])

    filtered = client.get("/api/v1/logs/audit?entity=trade", headers=ALICE).json()
    assert {r["entity"] for r in filtered["data"]} == {"trade"}
    assert client.get("/api/v1/logs/audit", headers=BOB).json()["total"] == 0  # isolation

    # The back-dated trade was not gated, and that decision is itself on record.
    signals = client.get("/api/v1/logs/signals", headers=ALICE).json()
    assert signals["total"] == 1 and signals["data"][0]["decision"] == "info"
    assert "back-dated" in signals["data"][0]["message"]
    assert client.get("/api/v1/logs/signals?decision=nope", headers=ALICE).status_code == 422

    # No way to alter history over HTTP.
    for method in ("put", "patch", "delete", "post"):
        for path in ("/api/v1/logs/audit", "/api/v1/logs/signals"):
            assert getattr(client, method)(path, headers=ALICE).status_code == 405


def test_market_tickers_symbols_param(client: TestClient) -> None:
    ok = client.get("/api/v1/market/tickers?symbols=spy,aapl")
    assert ok.status_code == 200 and ok.json()["source"] in ("live", "fallback")
    assert client.get("/api/v1/market/tickers?symbols=").status_code == 422
    assert client.get("/api/v1/market/tickers?symbols=BAD SYMBOL!").status_code == 422
    too_many = ",".join(f"S{i}" for i in range(30))
    assert client.get(f"/api/v1/market/tickers?symbols={too_many}").status_code == 422


def test_failed_login_is_logged(client: TestClient, monkeypatch) -> None:
    from fastapi import HTTPException

    from app.api.v1.endpoints import auth as auth_endpoints
    from app.config import settings

    events: list[tuple] = []
    monkeypatch.setattr(settings, "SUPABASE_URL", "https://x.supabase.co")
    monkeypatch.setattr(settings, "SUPABASE_ANON_KEY", "anon")
    monkeypatch.setattr(
        auth_endpoints.log, "warning", lambda event, **kw: events.append((event, kw))
    )

    async def reject(*a, **k):
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    monkeypatch.setattr(auth_endpoints, "_supabase_auth_request", reject)
    r = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "wrongpass1"})
    assert r.status_code == 400
    assert events == [("auth.login_failed", {"email": "a@example.com", "status": 400})]
    assert "wrongpass1" not in str(events)  # the password is never logged


def test_endpoints_require_authentication(client: TestClient) -> None:
    for path in (
        "/api/v1/portfolio",
        "/api/v1/trades",
        "/api/v1/trades/export.csv",
        "/api/v1/watchlists",
        "/api/v1/settings",
        "/api/v1/logs/audit",
        "/api/v1/logs/signals",
    ):
        assert client.get(path).status_code == 401, path

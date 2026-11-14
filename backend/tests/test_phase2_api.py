"""Phase 2: gate, entry enforcement, sizing, band usage, regime score and history."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app import database
from app.domain.regime_score import RegimeScore
from app.repositories.sql import Repo

ALICE = {"Authorization": "Bearer dev:alice"}
BOB = {"Authorization": "Bearer dev:bob"}
TODAY = date.today().isoformat()


def _portfolio(client: TestClient, headers=ALICE) -> str:
    return client.post("/api/v1/portfolio", headers=headers, json={"name": "P"}).json()[
        "portfolio_id"
    ]


def _entry(pid: str, **over) -> dict:
    body = {
        "portfolio_id": pid,
        "symbol": "AAPL",
        "trade_type": "put",
        "direction": "short",
        "entry_price": 2.0,
        "quantity": 1,
        "entry_date": TODAY,
        "strike": 190,
        "expiry": (date.today() + timedelta(days=40)).isoformat(),
        "layer": "base",
    }
    body.update(over)
    return body


def _post_trade(client, pid, headers=ALICE, **over):
    return client.post("/api/v1/trades", headers=headers, json=_entry(pid, **over))


def _gate(client, headers=ALICE) -> dict:
    return client.get("/api/v1/gate", headers=headers).json()["data"]


def _rules(data: dict) -> set[str]:
    return {r["rule_id"] for r in data["reasons"]}


def _signals(client, headers=ALICE, **params) -> dict:
    return client.get("/api/v1/logs/signals", headers=headers, params=params).json()


# ------------------------------------------------------------ master gate


def test_master_gate_is_clear_in_a_calm_uptrend(client: TestClient) -> None:
    data = _gate(client)
    assert data["clear"] is True and data["status"] == "CLEAR TO TRADE" and data["reasons"] == []
    assert data["regime"]["state"] == "GROWTH"
    assert data["layer_split"] == {"base": 40, "growth": 60} and data["growth_locked"] is False
    assert data["equity"] == 100000 and data["enforce_gate"] is True
    assert "BR-013" in data["not_evaluated"]


def test_master_gate_blocks_a_down_market(client: TestClient, regime_inputs) -> None:
    regime_inputs.falling_market()
    data = _gate(client)
    assert data["status"] == "BLOCKED" and "BR-010" in _rules(data)
    assert data["regime"]["state"] == "DEFENSIVE" and data["growth_locked"] is True


def test_master_gate_blocks_when_the_regime_cannot_be_computed(
    client: TestClient, regime_inputs
) -> None:
    regime_inputs.unavailable()
    data = _gate(client)
    assert data["status"] == "BLOCKED" and data["regime"]["state"] == "UNKNOWN"
    assert data["reasons"][0]["kind"] == "data" and data["growth_locked"] is True


def test_equity_guardrail_uses_realised_losses(client: TestClient) -> None:
    client.put("/api/v1/settings", headers=ALICE, json={"account_size": 10000, "min_equity": 9500})
    assert _gate(client)["clear"] is True and _gate(client)["equity"] == 10000

    pid = _portfolio(client)
    # Back-dated so it is not gated; short 10 contracts opened at 2.0, closed at 12.0 = -$100.
    t = _post_trade(client, pid, entry_date="2026-01-05", quantity=10).json()
    client.post(
        f"/api/v1/trades/{t['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 12.0, "exit_date": "2026-01-09"},
    )
    data = _gate(client)
    assert data["equity"] == 9900 and data["clear"] is True  # still above the 9,500 guardrail

    client.put("/api/v1/settings", headers=ALICE, json={"min_equity": 9950})
    assert "BR-012" in _rules(_gate(client))


# ------------------------------------------------------------ /gate/check


def test_gate_check_is_a_dry_run_that_does_not_log(client: TestClient, symbol_data) -> None:
    body = {
        "symbol": "aapl",
        "trade_type": "put",
        "layer": "base",
        "strike": 190,
        "expiry": (date.today() + timedelta(days=40)).isoformat(),
    }
    r = client.post("/api/v1/gate/check", headers=ALICE, json=body).json()["data"]
    assert r["clear"] is True and r["status"] == "CLEAR TO TRADE" and r["skipped"] is False
    assert symbol_data.calls[0][0] == "AAPL"  # symbol normalised
    assert (
        symbol_data.calls[0][1]["strike"] == 190 and symbol_data.calls[0][1]["option_type"] == "put"
    )
    assert _signals(client)["total"] == 0  # dry run: nothing written


@pytest.mark.parametrize(
    "change,rule",
    [
        ({"spread_pct": 12.0}, "BR-017"),
        ({"open_interest": 100}, "BR-018"),
        ({"market_cap": 1e9}, "BR-019"),
        ({"market_cap": 5e9}, "BR-042"),  # fine for Growth, too small for the Base layer
        ({"next_earnings": date.today() + timedelta(days=5)}, "BR-020"),
    ],
)
def test_gate_check_applies_each_symbol_rule(client, symbol_data, change, rule) -> None:
    for key, value in change.items():
        setattr(symbol_data.data, key, value)
    r = client.post(
        "/api/v1/gate/check", headers=ALICE, json={"symbol": "AAPL", "layer": "base"}
    ).json()["data"]
    assert r["clear"] is False and rule in _rules(r)


def test_gate_check_blocks_when_symbol_data_is_unavailable(client: TestClient, symbol_data) -> None:
    symbol_data.data.fetched = False
    r = client.post("/api/v1/gate/check", headers=ALICE, json={"symbol": "AAPL"}).json()["data"]
    assert r["status"] == "BLOCKED" and {x["kind"] for x in r["reasons"]} == {"data"}


def test_gate_check_skips_old_entry_dates(client: TestClient, symbol_data) -> None:
    old = (date.today() - timedelta(days=30)).isoformat()
    r = client.post(
        "/api/v1/gate/check", headers=ALICE, json={"symbol": "AAPL", "entry_date": old}
    ).json()["data"]
    assert r["skipped"] is True and r["clear"] is True and symbol_data.calls == []
    yesterday = (
        date.today() - timedelta(days=1)
    ).isoformat()  # within the 1-day grace: still gated
    r = client.post(
        "/api/v1/gate/check", headers=ALICE, json={"symbol": "AAPL", "entry_date": yesterday}
    ).json()["data"]
    assert r["skipped"] is False and len(symbol_data.calls) == 1


# -------------------------------------------------- enforcement on trades


def test_a_clear_entry_is_recorded_and_logged_as_allowed(client: TestClient) -> None:
    pid = _portfolio(client)
    r = _post_trade(client, pid)
    assert r.status_code == 201, r.text
    sig = _signals(client)["data"]
    assert len(sig) == 1 and sig[0]["decision"] == "allowed" and sig[0]["symbol"] == "AAPL"
    assert (
        "BR-017" in sig[0]["details"]["checked"] and "BR-013" in sig[0]["details"]["not_evaluated"]
    )


def test_a_blocked_entry_is_refused_with_every_reason_and_nothing_is_created(
    client, symbol_data
) -> None:
    symbol_data.data.spread_pct = 15.0
    symbol_data.data.open_interest = 50
    pid = _portfolio(client)
    r = _post_trade(client, pid)

    assert r.status_code == 409
    err = r.json()["error"]
    assert r.json()["success"] is False and err["message"] == "Trade blocked by Do-Not-Trade rules"
    assert {x["rule_id"] for x in err["details"]["reasons"]} == {"BR-017", "BR-018"}
    assert client.get("/api/v1/trades", headers=ALICE).json()["total"] == 0  # no trade was created

    blocked = _signals(client, decision="blocked")
    assert blocked["total"] == 2 and {s["rule_id"] for s in blocked["data"]} == {"BR-017", "BR-018"}
    assert _signals(client, rule_id="BR-017")["total"] == 1  # filterable by rule (FR-730)


def test_missing_data_blocks_the_entry(client: TestClient, symbol_data) -> None:
    symbol_data.data.fetched = False
    r = _post_trade(client, _portfolio(client))
    assert r.status_code == 409
    assert all(x["kind"] == "data" for x in r.json()["error"]["details"]["reasons"])


def test_a_down_market_blocks_every_new_entry(client: TestClient, regime_inputs) -> None:
    regime_inputs.falling_market()
    r = _post_trade(client, _portfolio(client))
    assert r.status_code == 409
    assert "BR-010" in {x["rule_id"] for x in r.json()["error"]["details"]["reasons"]}


def test_enforcement_can_be_switched_off_in_settings(
    client: TestClient, symbol_data, regime_inputs
) -> None:
    regime_inputs.falling_market()
    symbol_data.data.spread_pct = 50.0
    client.put("/api/v1/settings", headers=ALICE, json={"enforce_gate": False})
    r = _post_trade(client, _portfolio(client))
    assert r.status_code == 201 and symbol_data.calls == []
    assert _signals(client)["total"] == 0


def test_backdated_entries_are_recorded_without_the_gate(
    client: TestClient, symbol_data, regime_inputs
) -> None:
    regime_inputs.falling_market()  # would block a new entry
    r = _post_trade(client, _portfolio(client), entry_date="2026-01-05")
    assert r.status_code == 201 and symbol_data.calls == []
    assert _signals(client)["data"][0]["decision"] == "info"


def test_stock_trades_skip_option_liquidity_rules(client: TestClient, symbol_data) -> None:
    symbol_data.data.spread_pct = None
    symbol_data.data.open_interest = None
    r = _post_trade(
        client, _portfolio(client), trade_type="stock", direction="long", strike=None, expiry=None
    )
    assert r.status_code == 201


# ----------------------------------------------------------- news flag


def test_news_flag_blocks_then_unblocks_a_symbol(client: TestClient) -> None:
    pid = _portfolio(client)
    flag = client.put(
        "/api/v1/symbols/aapl/flag", headers=ALICE, json={"news_flag": True, "note": "probe"}
    )
    assert flag.json()["data"] == {"symbol": "AAPL", "news_flag": True, "note": "probe"}

    r = _post_trade(client, pid)
    assert r.status_code == 409
    assert [x["rule_id"] for x in r.json()["error"]["details"]["reasons"]] == ["BR-021"]

    assert _post_trade(client, pid, symbol="MSFT").status_code == 201  # other symbols unaffected

    client.put("/api/v1/symbols/AAPL/flag", headers=ALICE, json={"news_flag": False})
    assert _post_trade(client, pid).status_code == 201


def test_flags_are_private_to_each_user_and_validated(client: TestClient) -> None:
    client.put("/api/v1/symbols/AAPL/flag", headers=ALICE, json={"news_flag": True})
    assert (
        client.get("/api/v1/symbols/flags", headers=ALICE).json()["data"]["AAPL"]["news_flag"]
        is True
    )
    assert client.get("/api/v1/symbols/flags", headers=BOB).json()["data"] == {}
    assert (
        _post_trade(client, _portfolio(client, BOB), BOB).status_code == 201
    )  # Bob is not blocked
    assert (
        client.put(
            "/api/v1/symbols/B%40D!/flag", headers=ALICE, json={"news_flag": True}
        ).status_code
        == 422
    )


# ------------------------------------------------------- growth layer lock


def _defensive_but_tradeable(client: TestClient, regime_inputs) -> None:
    """Regime score ~30 (DEFENSIVE) with the market still above its 200-day average."""
    regime_inputs.vix = [60.0] * 249 + [40.0]
    client.put(
        "/api/v1/settings",
        headers=ALICE,
        json={"regime_weights": {"trend": 30, "vix": 40, "iv_rank": 30}},
    )


def test_growth_layer_is_locked_in_a_defensive_regime_but_base_is_not(
    client, regime_inputs
) -> None:
    _defensive_but_tradeable(client, regime_inputs)
    gate = _gate(client)
    assert gate["regime"]["state"] == "DEFENSIVE" and gate["clear"] is True  # score is above 25
    pid = _portfolio(client)

    growth = _post_trade(client, pid, layer="growth")
    assert growth.status_code == 409
    assert [x["rule_id"] for x in growth.json()["error"]["details"]["reasons"]] == ["BR-023"]
    assert _post_trade(client, pid, layer="base").status_code == 201


# ------------------------------------------------------------------ sizing


def test_sizing_uses_settings_regime_and_the_chosen_mode(client: TestClient) -> None:
    r = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "base", "max_loss_per_contract": 500},
    ).json()["data"]
    assert (r["mode"], r["risk_budget"], r["quantity"], r["risk_amount"]) == (
        "max_loss",
        1250.0,
        2,
        1000.0,
    )
    assert r["regime_state"] == "GROWTH" and r["layer_split"] == {"base": 40, "growth": 60}
    assert r["account_size"] == 100000

    credit = client.post(
        "/api/v1/sizing/calculate", headers=ALICE, json={"layer": "base", "credit": 2.0}
    ).json()["data"]
    assert credit["mode"] == "credit" and credit["quantity"] == 6


def test_sizing_follows_account_size_and_risk_overrides(client: TestClient) -> None:
    client.put(
        "/api/v1/settings", headers=ALICE, json={"account_size": 50000, "base_risk_pct": 1.0}
    )
    r = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "base", "max_loss_per_contract": 250},
    ).json()["data"]
    assert r["risk_budget"] == 500.0 and r["quantity"] == 2
    o = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "base", "max_loss_per_contract": 250, "risk_pct": 2},
    ).json()["data"]
    assert o["risk_budget"] == 1000.0 and o["quantity"] == 4
    assert any("outside the documented base range" in w for w in o["warnings"])


def test_sizing_tightens_and_locks_in_a_defensive_regime(client, regime_inputs) -> None:
    _defensive_but_tradeable(client, regime_inputs)
    base = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "base", "max_loss_per_contract": 500},
    ).json()["data"]
    assert base["risk_budget"] == 625.0 and base["quantity"] == 1
    growth = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "growth", "max_loss_per_contract": 500},
    ).json()["data"]
    assert growth["blocked"] is True and growth["reasons"][0]["rule_id"] == "BR-023"


def test_sizing_respects_band_caps_from_open_trades(client: TestClient) -> None:
    client.put(
        "/api/v1/settings",
        headers=ALICE,
        json={"band_caps": {"A": 1, "B": 25, "C": 20, "D": 15, "E": 10}},
    )
    pid = _portfolio(client)
    _post_trade(
        client, pid, entry_date="2026-01-05", band="A", risk_amount=900
    )  # open, $900 in band A
    r = client.post(
        "/api/v1/sizing/calculate",
        headers=ALICE,
        json={"layer": "base", "max_loss_per_contract": 500, "band": "A"},
    ).json()["data"]
    # Band A cap = 1% of $100k = $1,000; $900 used -> room for $100 -> not even one $500 contract.
    assert r["blocked"] is True and r["reasons"][0]["rule_id"] == "BR-034"


def test_sizing_validation(client: TestClient) -> None:
    for body in (
        {"layer": "yolo"},
        {"layer": "base", "credit": -1},
        {"layer": "base", "band": "Z"},
        {"layer": "base", "risk_pct": 50},
    ):
        assert client.post("/api/v1/sizing/calculate", headers=ALICE, json=body).status_code == 422


# -------------------------------------------------------------- band usage


def test_band_usage_counts_open_trades_only(client: TestClient) -> None:
    pid = _portfolio(client)
    a = _post_trade(client, pid, entry_date="2026-01-05", band="A", risk_amount=20000).json()
    _post_trade(client, pid, symbol="MSFT", entry_date="2026-01-05", band="B", risk_amount=21000)
    _post_trade(
        client, pid, symbol="TSLA", entry_date="2026-01-05", band="B", risk_amount=None
    )  # ignored
    closed = _post_trade(
        client, pid, symbol="NVDA", entry_date="2026-01-05", band="C", risk_amount=9000
    ).json()
    client.post(
        f"/api/v1/trades/{closed['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 1, "exit_date": "2026-01-09"},
    )

    rows = {
        r["band"]: r for r in client.get("/api/v1/portfolio/bands", headers=ALICE).json()["data"]
    }
    assert rows["A"]["exposure_pct"] == 20.0 and rows["A"]["status"] == "ok"
    assert (
        rows["B"]["exposure_pct"] == 21.0 and rows["B"]["status"] == "near"
    )  # >= 80% of the 25% cap
    assert rows["C"]["exposure"] == 0 and rows["D"]["cap_pct"] == 15.0
    assert a["band"] == "A"
    assert client.get("/api/v1/portfolio/bands", headers=BOB).json()["data"][0]["exposure"] == 0


# ------------------------------------------------------------ regime score


def test_regime_score_endpoint_and_history(client: TestClient) -> None:
    data = client.get("/api/v1/regime/score", headers=ALICE).json()["data"]
    assert data["state"] == "GROWTH" and data["source"] == "live" and data["score"] > 90
    assert set(data["components"]) == {"trend", "vix", "iv_rank"}

    hist = client.get("/api/v1/regime/history", headers=ALICE).json()["data"]
    assert len(hist) == 1 and hist[0]["as_of"] == TODAY and hist[0]["state"] == "GROWTH"

    client.get("/api/v1/regime/score", headers=ALICE)  # same day again: updates, no duplicate row
    assert len(client.get("/api/v1/regime/history", headers=ALICE).json()["data"]) == 1
    assert client.get("/api/v1/regime/history?limit=0", headers=ALICE).status_code == 422


def test_users_weights_change_their_score_but_not_the_shared_history(
    client: TestClient, regime_inputs
) -> None:
    regime_inputs.vix = [30.0] * 250
    client.put(
        "/api/v1/settings",
        headers=ALICE,
        json={"regime_weights": {"trend": 0, "vix": 100, "iv_rank": 0}},
    )
    mine = client.get("/api/v1/regime/score", headers=ALICE).json()["data"]
    assert mine["score"] == pytest.approx(35.7, abs=0.1) and mine["state"] == "DEFENSIVE"
    stored = client.get("/api/v1/regime/history", headers=ALICE).json()["data"][0]
    assert stored["weights"] == {"trend": 40.0, "vix": 30.0, "iv_rank": 30.0}  # default weights
    other = client.get("/api/v1/regime/score", headers=BOB).json()["data"]
    assert other["score"] > 70  # Bob keeps the defaults


def test_a_state_change_is_written_to_the_signal_log(client: TestClient) -> None:
    async def seed_yesterday() -> None:
        async with database.get_session() as s:
            await Repo(s).save_regime(
                RegimeScore(
                    score=30.0,
                    state="DEFENSIVE",
                    components={},
                    weights={},
                    source="live",
                    as_of=(date.today() - timedelta(days=1)).isoformat(),
                )
            )

    asyncio.run(seed_yesterday())
    client.get("/api/v1/regime/score", headers=ALICE)
    changes = _signals(client, ALICE)["data"]
    assert len(changes) == 1 and changes[0]["kind"] == "regime"
    assert changes[0]["message"] == "Regime changed from DEFENSIVE to GROWTH."
    client.get("/api/v1/regime/score", headers=ALICE)  # no further change, no further entry
    assert _signals(client)["total"] == 1


def test_unavailable_inputs_never_invent_or_overwrite_a_score(
    client: TestClient, regime_inputs
) -> None:
    regime_inputs.unavailable()
    data = client.get("/api/v1/regime/score", headers=ALICE).json()["data"]
    assert data["state"] == "UNKNOWN" and data["score"] is None and data["source"] == "unavailable"
    assert client.get("/api/v1/regime/history", headers=ALICE).json()["data"] == []


def test_falls_back_to_the_stored_score_when_live_data_is_down(
    client: TestClient, regime_inputs
) -> None:
    client.get("/api/v1/regime/score", headers=ALICE)  # stores today's GROWTH score
    regime_inputs.unavailable()
    regime_service_clear()
    data = client.get("/api/v1/regime/score", headers=ALICE).json()["data"]
    assert data["source"] == "stored" and data["state"] == "GROWTH"


def regime_service_clear() -> None:
    from app.services import regime_service

    regime_service.clear_cache()


def test_regime_inputs_are_cached_between_requests(client: TestClient, monkeypatch) -> None:
    from app.domain import regime_score as rs

    calls = []
    inputs = ([100 + i * 0.5 for i in range(250)], [15.0] * 250)
    monkeypatch.setattr(rs, "fetch_inputs", lambda: calls.append(1) or inputs)
    regime_service_clear()
    for _ in range(3):
        client.get("/api/v1/regime/score", headers=ALICE)
    assert len(calls) == 1


def test_phase2_endpoints_require_authentication(client: TestClient) -> None:
    for method, path in (
        ("get", "/api/v1/gate"),
        ("post", "/api/v1/gate/check"),
        ("post", "/api/v1/sizing/calculate"),
        ("get", "/api/v1/regime/score"),
        ("get", "/api/v1/regime/history"),
        ("get", "/api/v1/portfolio/bands"),
        ("get", "/api/v1/symbols/flags"),
        ("put", "/api/v1/symbols/AAPL/flag"),
    ):
        assert getattr(client, method)(path).status_code == 401, path

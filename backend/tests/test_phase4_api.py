"""Phase 4: portfolio risk, scenarios, strategy matrix, option chain, EV ranking, calibration."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.domain.alerts import MarketInput
from app.main import app
from app.services.screener import get_chain_provider

ALICE = {"Authorization": "Bearer dev:alice"}
BOB = {"Authorization": "Bearer dev:bob"}
OLD = "2026-01-05"  # back-dated: recorded without the entry gate
EXPIRY = (date.today() + timedelta(days=30)).isoformat()


def _portfolio(client: TestClient, headers=ALICE) -> str:
    return client.post("/api/v1/portfolio", headers=headers, json={"name": "P"}).json()[
        "portfolio_id"
    ]


def _open(client, pid, headers=ALICE, **over) -> dict:
    body = {
        "portfolio_id": pid,
        "symbol": "AAPL",
        "trade_type": "put",
        "direction": "short",
        "entry_price": 2.0,
        "quantity": 1,
        "entry_date": OLD,
        "strike": 190,
        "expiry": EXPIRY,
        "layer": "base",
        "risk_amount": 1000,
    }
    body.update(over)
    r = client.post("/api/v1/trades", headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _risk(client, headers=ALICE) -> dict:
    r = client.get("/api/v1/portfolio/risk", headers=headers)
    assert r.status_code == 200, r.text
    return r.json()["data"]


# ---------------------------------------------------------------- portfolio risk


def test_risk_with_no_positions(client: TestClient) -> None:
    d = _risk(client)
    assert d["capital_at_risk"] == 0 and d["margin_pct"] == 0 and d["net_delta"] == 0
    assert d["open_positions"] == 0 and d["breaches"] == [] and d["sectors"] == []
    assert d["limits"]["capital_at_risk_pct"] == 50.0 and d["regime_state"] == "GROWTH"


def test_risk_adds_up_net_delta_margin_and_sectors(client: TestClient) -> None:
    pid = _portfolio(client)
    _open(client, pid, symbol="AAPL", risk_amount=4000)
    _open(client, pid, symbol="MSFT", risk_amount=2000)
    _open(client, pid, symbol="XOM", risk_amount=1000)
    d = _risk(client)
    assert d["capital_at_risk"] == 7000 and d["margin_pct"] == 7.0 and d["open_positions"] == 3
    assert d["net_delta"] == 45.0  # three short puts at delta -0.15: +15 each
    assert d["net_delta_dollars"] == 9000.0  # 45 x spot 200
    assert d["unpriced_positions"] == 0 and d["breaches"] == []
    tech, energy = d["sectors"]
    assert (tech["sector"], tech["capital_at_risk"], tech["pct_of_risk"]) == (
        "Technology",
        6000,
        85.7,
    )
    assert energy["sector"] == "Energy"


def test_unknown_sector_and_unpriced_positions_are_reported(
    client: TestClient, position_data, sectors
) -> None:
    pid = _portfolio(client)
    _open(client, pid, symbol="ZZZZ", risk_amount=500)
    position_data.unavailable = True
    d = _risk(client)
    assert d["unpriced_positions"] == 1 and d["net_delta"] == 0
    assert d["sectors"][0]["sector"] == "Unknown"


def test_sector_concentration_is_flagged(client: TestClient) -> None:
    pid = _portfolio(client)
    _open(client, pid, symbol="AAPL", risk_amount=15000)
    _open(client, pid, symbol="MSFT", risk_amount=15000)
    d = _risk(client)
    assert [b["code"] for b in d["breaches"]] == ["sector"]
    assert d["breaches"][0]["rule_id"] == "BR-080" and "Technology" in d["breaches"][0]["message"]


def test_risk_is_per_user(client: TestClient) -> None:
    _open(client, _portfolio(client), risk_amount=4000)
    assert _risk(client, BOB)["capital_at_risk"] == 0


# ------------------------------------------- BR-081 blocks new entries over the limit


def test_total_risk_over_the_limit_blocks_the_gate_br081(client: TestClient) -> None:
    pid = _portfolio(client)
    gate = client.get("/api/v1/gate", headers=ALICE).json()["data"]
    assert gate["clear"] is True and "BR-081" in gate["checked"]

    _open(client, pid, symbol="XOM", risk_amount=40000)  # 40% of the 100,000 account
    assert client.get("/api/v1/gate", headers=ALICE).json()["data"]["clear"] is True
    _open(client, pid, symbol="XOM", risk_amount=20000)  # 60%: over the 50% limit
    gate = client.get("/api/v1/gate", headers=ALICE).json()["data"]
    assert gate["status"] == "BLOCKED" and "BR-081" in {r["rule_id"] for r in gate["reasons"]}

    blocked = client.post(
        "/api/v1/trades",
        headers=ALICE,
        json={
            "portfolio_id": pid,
            "symbol": "AAPL",
            "trade_type": "put",
            "direction": "short",
            "entry_price": 2.0,
            "quantity": 1,
            "entry_date": date.today().isoformat(),
            "strike": 190,
            "expiry": EXPIRY,
            "layer": "base",
        },
    )
    assert blocked.status_code == 409


# ------------------------------------------------------------------- scenarios


@pytest.fixture
def priced(position_data):
    """AAPL quotes with an implied volatility so scenarios can reprice it."""
    position_data.by_symbol["AAPL"] = MarketInput(
        available=True, spot=200.0, mark=2.0, delta=-0.2, theta=0.05, iv=0.3
    )
    return position_data


def _run(client, headers=ALICE, **body) -> dict:
    r = client.post("/api/v1/scenarios/run", headers=headers, json=body)
    assert r.status_code == 200, r.text
    return r.json()["data"]


def test_scenario_with_no_positions(client: TestClient) -> None:
    d = _run(client, spot_pct=-10)
    assert d["positions"] == [] and d["total_change"] == 0 and len(d["ladder"]) == 7


def test_scenario_reprices_a_short_put(client: TestClient, priced) -> None:
    _open(client, _portfolio(client))
    down = _run(client, spot_pct=-10)
    (p,) = down["positions"]
    assert p["priced"] and p["current_pnl"] == 0.0 and p["change"] < -100
    assert down["total_change"] == p["change"] and down["unpriced"] == 0
    up = _run(client, spot_pct=10)
    assert up["total_change"] > 0
    ladder = [pt["total_change"] for pt in down["ladder"]]
    assert ladder == sorted(ladder) and down["ladder"][0]["spot_pct"] == -20


def test_scenario_reports_positions_it_cannot_price(client: TestClient) -> None:
    _open(client, _portfolio(client))  # the default fake quote has no implied volatility
    d = _run(client, spot_pct=-10)
    assert d["priced"] == 0 and d["unpriced"] == 1
    assert d["positions"][0]["reason"] == "no implied volatility" and d["total_change"] == 0


@pytest.mark.parametrize(
    "body",
    [{"spot_pct": -95}, {"spot_pct": 250}, {"iv_shift": 2}, {"days_forward": -1}],
)
def test_scenario_rejects_out_of_range_shocks(client: TestClient, body) -> None:
    assert client.post("/api/v1/scenarios/run", headers=ALICE, json=body).status_code == 422


def test_save_list_and_delete_scenarios(client: TestClient) -> None:
    body = {"name": "Crash", "spot_pct": -20, "iv_shift": 0.15, "days_forward": 5}
    saved = client.post("/api/v1/scenarios", headers=ALICE, json=body)
    assert saved.status_code == 201
    sid = saved.json()["data"]["id"]
    assert saved.json()["data"]["params"] == {"spot_pct": -20, "iv_shift": 0.15, "days_forward": 5}

    assert client.post("/api/v1/scenarios", headers=ALICE, json=body).status_code == 409
    assert [s["name"] for s in client.get("/api/v1/scenarios", headers=ALICE).json()["data"]] == [
        "Crash"
    ]
    assert client.get("/api/v1/scenarios", headers=BOB).json()["data"] == []
    assert client.delete(f"/api/v1/scenarios/{sid}", headers=BOB).status_code == 404
    assert client.delete(f"/api/v1/scenarios/{sid}", headers=ALICE).status_code == 204
    assert client.get("/api/v1/scenarios", headers=ALICE).json()["data"] == []

    audit = client.get("/api/v1/logs/audit", headers=ALICE).json()["data"]
    assert {"scenario.save", "scenario.delete"} <= {row["action"] for row in audit}


def test_saving_needs_a_name(client: TestClient) -> None:
    assert client.post("/api/v1/scenarios", headers=ALICE, json={"spot_pct": -5}).status_code == 422
    assert client.post("/api/v1/scenarios", headers=ALICE, json={"name": ""}).status_code == 422


# --------------------------------------------------------------- strategy matrix


def test_matrix_shape_and_current_regime(client: TestClient) -> None:
    d = client.get("/api/v1/strategy-matrix", headers=ALICE).json()["data"]
    assert d["regimes"] == ["DEFENSIVE", "NORMAL", "GROWTH"] and len(d["rows"]) == 6
    assert d["current_regime"] == "GROWTH" and d["gate_clear"] is True
    assert all(r["cells"]["GROWTH"]["gate"] == "clear" for r in d["rows"])


def test_matrix_is_blocked_while_the_gate_is_blocked(client: TestClient, regime_inputs) -> None:
    regime_inputs.falling_market()
    d = client.get("/api/v1/strategy-matrix", headers=ALICE).json()["data"]
    assert d["gate_clear"] is False and d["gate_reasons"]
    cur = d["current_regime"]
    assert all(r["cells"][cur]["availability"] == "blocked" for r in d["rows"])


def test_matrix_filters_and_validation(client: TestClient) -> None:
    d = client.get("/api/v1/strategy-matrix?layer=growth&band=E", headers=ALICE).json()["data"]
    ic = next(r for r in d["rows"] if r["strategy"] == "Iron Condor")
    assert ic["cells"]["NORMAL"]["filtered"] is True
    assert client.get("/api/v1/strategy-matrix?layer=nope", headers=ALICE).status_code == 422
    assert client.get("/api/v1/strategy-matrix?band=Z", headers=ALICE).status_code == 422


# ------------------------------------------------------------------ option chain


def _row(strike, option_type, expiry, delta):
    return {
        "symbol": "AAPL",
        "strike": strike,
        "expiry": expiry,
        "option_type": option_type,
        "bid": 1.0,
        "ask": 1.2,
        "last_price": 1.1,
        "implied_vol": 0.3,
        "delta": delta,
        "gamma": 0.01,
        "theta": -0.05,
        "vega": 0.1,
        "open_interest": 500,
        "volume": 20,
    }


@pytest.fixture
def chain_provider():
    soon = (date.today() + timedelta(days=7)).isoformat()
    later = (date.today() + timedelta(days=35)).isoformat()
    rows = [
        _row(190, "put", soon, -0.25),
        _row(190, "call", soon, 0.75),
        _row(200, "put", soon, -0.5),
        _row(200, "call", soon, 0.5),
        _row(200, "call", later, 0.55),
    ]
    state = {"source": "live", "rows": rows, "symbols": []}

    def provider(symbol: str):
        state["symbols"].append(symbol)
        return 201.0, state["rows"], state["source"]

    app.dependency_overrides[get_chain_provider] = lambda: provider
    yield state, soon, later
    app.dependency_overrides.pop(get_chain_provider, None)


def test_chain_groups_calls_and_puts_by_strike(client: TestClient, chain_provider) -> None:
    state, soon, later = chain_provider
    d = client.get("/api/v1/options/chain?symbol=aapl", headers=ALICE).json()["data"]
    assert state["symbols"] == ["AAPL"]
    assert d["spot"] == 201.0 and d["source"] == "live" and d["expiry"] == soon and d["dte"] == 7
    assert d["expiries"] == [soon, later]
    assert [s["strike"] for s in d["strikes"]] == [190, 200]
    s190 = d["strikes"][0]
    assert s190["put"]["delta"] == -0.25 and s190["put"]["pop_short"] == 0.75
    assert s190["call"]["pop_short"] == 0.25 and s190["put"]["open_interest"] == 500


def test_chain_for_another_expiry_and_missing_sides(client: TestClient, chain_provider) -> None:
    _state, _soon, later = chain_provider
    d = client.get(f"/api/v1/options/chain?symbol=AAPL&expiry={later}", headers=ALICE).json()[
        "data"
    ]
    assert d["expiry"] == later and len(d["strikes"]) == 1
    assert d["strikes"][0]["put"] is None and d["strikes"][0]["call"]["delta"] == 0.55


def test_chain_labels_synthetic_data_and_handles_errors(client: TestClient, chain_provider) -> None:
    state, _soon, _later = chain_provider
    state["source"] = "synthetic"
    assert (
        client.get("/api/v1/options/chain?symbol=AAPL", headers=ALICE).json()["data"]["source"]
        == "synthetic"
    )
    missing = client.get("/api/v1/options/chain?symbol=AAPL&expiry=2030-01-01", headers=ALICE)
    assert missing.status_code == 404
    state["rows"] = []
    assert client.get("/api/v1/options/chain?symbol=AAPL", headers=ALICE).status_code == 404
    assert client.get("/api/v1/options/chain", headers=ALICE).status_code == 422


def test_chain_needs_login(client: TestClient) -> None:
    assert client.get("/api/v1/options/chain?symbol=AAPL").status_code in (401, 403)


# ------------------------------------------------------------------- EV and picks


def test_picks_are_ranked_by_expected_value(client: TestClient) -> None:
    from tests.test_phase3_api import _seed_picks  # reuse the seeded weekly picks

    _seed_picks()
    body = client.get("/api/v1/picks", headers=ALICE).json()
    assert [p["symbol"] for p in body["data"]] == ["MSFT", "AAPL", "TSLA"]
    assert body["data"][0]["ev"] > body["data"][1]["ev"] > body["data"][2]["ev"]
    assert body["data"][0]["ev"] == pytest.approx(0.88 * 150 - 0.12 * 100)


# -------------------------------------------------------------------- calibration


def test_calibration_reports_realised_results_by_layer(client: TestClient) -> None:
    empty = client.get("/api/v1/analytics/ev-calibration", headers=ALICE).json()["data"]
    assert empty["groups"] == [] and empty["total_trades"] == 0 and empty["note"]

    pid = _portfolio(client)
    win = _open(client, pid, layer="base")
    lose = _open(client, pid, symbol="MSFT", layer="base")
    other = _open(client, pid, symbol="XOM", layer="growth")
    for t, exit_price in ((win, 0.5), (lose, 4.0), (other, 1.0)):
        r = client.post(
            f"/api/v1/trades/{t['trade_id']}/close",
            headers=ALICE,
            json={"exit_price": exit_price, "exit_date": date.today().isoformat()},
        )
        assert r.status_code == 200, r.text

    d = client.get("/api/v1/analytics/ev-calibration", headers=ALICE).json()["data"]
    assert d["total_trades"] == 3
    base = next(g for g in d["groups"] if g["group"] == "base")
    assert base["trades"] == 2 and base["win_rate"] == 50.0
    assert base["avg_pnl"] == pytest.approx(((2.0 - 0.5) * 100 + (2.0 - 4.0) * 100) / 2)
    assert base["avg_expected"] is None
    assert (
        client.get("/api/v1/analytics/ev-calibration", headers=BOB).json()["data"]["total_trades"]
        == 0
    )

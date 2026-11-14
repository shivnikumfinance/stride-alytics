"""Phase 3: exit alerts and acknowledgements, BR-011 in the gate, picks, dashboard summary."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app import database
from app import models as m
from app.domain.alerts import MarketInput

ALICE = {"Authorization": "Bearer dev:alice"}
BOB = {"Authorization": "Bearer dev:bob"}
OLD = "2026-01-05"  # back-dated: recorded without the entry gate


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
        "expiry": (date.today() + timedelta(days=30)).isoformat(),
        "layer": "base",
    }
    body.update(over)
    r = client.post("/api/v1/trades", headers=headers, json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _exits(client, headers=ALICE, **params) -> dict:
    return client.get("/api/v1/alerts/exits", headers=headers, params=params).json()["data"]


def _ack(client, trade_id: str, code: str, headers=ALICE):
    return client.post(
        "/api/v1/alerts/ack", headers=headers, json={"trade_id": trade_id, "code": code}
    )


# 5.3% in the money with delta -0.8; mark 3.00 is a 50% loss on a 2.00 credit, which is only a
# "watch", so the assignment alarm is the single critical reason and decides the action.
ASSIGNMENT = MarketInput(available=True, spot=180.0, mark=3.0, delta=-0.8, theta=0.1)


# ------------------------------------------------------------ exit alerts


def test_no_open_positions_means_no_alerts(client: TestClient) -> None:
    data = _exits(client)
    assert data["alerts"] == [] and data["open_positions"] == 0
    assert data["summary"] == {"normal": 0, "watch": 0, "warning": 0, "critical": 0}
    assert data["unacknowledged_critical"] == 0 and data["regime"]["state"] == "GROWTH"


def test_a_calm_position_is_normal_and_only_listed_when_asked(client: TestClient) -> None:
    _open(client, _portfolio(client))
    assert _exits(client)["alerts"] == []  # default min_severity is "watch"
    data = _exits(client, min_severity="normal")
    (a,) = data["alerts"]
    assert a["severity"] == "normal" and a["action"] == "hold" and a["reasons"] == []
    assert a["pnl"] == 10.0 and a["pnl_pct"] == 0.05 and a["dte"] == 30  # (2.00 - 1.90) x 100
    assert a["delta"] == -0.15 and a["position_delta"] == 15.0 and a["theta"] == 0.04
    assert data["summary"]["normal"] == 1 and data["open_positions"] == 1


def test_positions_are_sorted_most_urgent_first(client: TestClient, position_data) -> None:
    pid = _portfolio(client)
    _open(client, pid, symbol="MSFT")
    _open(client, pid, symbol="TSLA")
    _open(client, pid, symbol="AAPL")
    position_data.by_symbol["TSLA"] = MarketInput(
        available=True, spot=200, mark=3.0, delta=-0.4
    )  # watch
    position_data.by_symbol["AAPL"] = ASSIGNMENT  # critical
    alerts = _exits(client, min_severity="normal")["alerts"]
    assert [(a["symbol"], a["severity"]) for a in alerts] == [
        ("AAPL", "critical"),
        ("TSLA", "watch"),
        ("MSFT", "normal"),
    ]


def test_an_assignment_alarm_is_critical_with_reasons_and_a_roll_suggestion(
    client, position_data
) -> None:
    _open(client, _portfolio(client))
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    (a,) = _exits(client)["alerts"]
    assert a["severity"] == "critical" and a["assignment_risk"] is True and a["action"] == "roll"
    assert {r["code"] for r in a["reasons"]} >= {"assignment_risk"}
    assert all(r["rule_id"] for r in a["reasons"] if r["severity"] == "critical")
    assert a["unacknowledged_critical"] is True


def test_unavailable_prices_are_flagged_not_guessed(client: TestClient, position_data) -> None:
    _open(client, _portfolio(client))
    position_data.unavailable = True
    (a,) = _exits(client)["alerts"]
    assert a["severity"] == "watch" and a["data_available"] is False
    assert [r["code"] for r in a["reasons"]] == ["no_market_data"]
    assert a["pnl"] is None and a["delta"] is None


def test_a_deteriorated_regime_warns_on_every_open_position(
    client: TestClient, regime_inputs
) -> None:
    regime_inputs.falling_market()
    client.put(
        "/api/v1/settings",
        headers=ALICE,
        json={"regime_weights": {"trend": 50, "vix": 50, "iv_rank": 0}},
    )
    pid = _portfolio(client)
    _open(client, pid, layer="growth")
    _open(client, pid, symbol="MSFT", layer="base")
    by = {a["symbol"]: a for a in _exits(client)["alerts"]}
    assert by["AAPL"]["severity"] == "warning" and by["AAPL"]["action"] == "close"  # Growth: close
    assert by["MSFT"]["action"] == "hedge"  # Base: hedge
    assert any(r["rule_id"] == "BR-051" for r in by["AAPL"]["reasons"])


def test_alerts_are_private_and_the_filter_is_validated(client: TestClient, position_data) -> None:
    _open(client, _portfolio(client))
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    assert _exits(client, BOB)["alerts"] == []
    assert client.get("/api/v1/alerts/exits?min_severity=nope", headers=ALICE).status_code == 422


# ------------------------------------------------------------ acknowledgements


def test_acknowledging_a_critical_alert(client: TestClient, position_data) -> None:
    t = _open(client, _portfolio(client))
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    assert _exits(client)["unacknowledged_critical"] == 1

    r = _ack(client, t["trade_id"], "assignment_risk")
    assert r.status_code == 200 and r.json()["data"]["severity"] == "critical"

    data = _exits(client)
    (a,) = data["alerts"]
    reason = next(x for x in a["reasons"] if x["code"] == "assignment_risk")
    assert reason["acknowledged"] is True and a["unacknowledged_critical"] is False
    assert data["unacknowledged_critical"] == 0
    assert a["severity"] == "critical"  # acknowledging does not hide or lower the alert

    again = _ack(client, t["trade_id"], "assignment_risk")  # idempotent
    assert again.json()["data"]["id"] == r.json()["data"]["id"]
    assert client.get("/api/v1/alerts/acks", headers=ALICE).json()["total"] == 1

    audit = client.get("/api/v1/logs/audit?action=alert.ack", headers=ALICE).json()
    assert audit["total"] == 1 and audit["data"][0]["after"]["code"] == "assignment_risk"


def test_you_can_only_acknowledge_an_active_alert_on_your_own_open_trade(
    client, position_data
) -> None:
    t = _open(client, _portfolio(client))
    assert _ack(client, t["trade_id"], "assignment_risk").status_code == 404  # not firing now
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    assert _ack(client, t["trade_id"], "made_up_code").status_code == 404
    assert _ack(client, t["trade_id"], "assignment_risk", BOB).status_code == 404  # not Bob's trade
    assert (
        client.post(
            "/api/v1/alerts/ack", headers=ALICE, json={"trade_id": "nope", "code": "x"}
        ).status_code
        == 422
    )
    assert _ack(client, t["trade_id"], "assignment_risk").status_code == 200


def test_a_recurring_alert_must_be_acknowledged_again(client: TestClient, position_data) -> None:
    t = _open(client, _portfolio(client))
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    _ack(client, t["trade_id"], "assignment_risk")
    assert _exits(client)["unacknowledged_critical"] == 0

    position_data.by_symbol.pop("AAPL")  # the condition clears
    assert _exits(client, min_severity="normal")["alerts"][0]["severity"] == "normal"
    (ack,) = client.get("/api/v1/alerts/acks", headers=ALICE).json()["data"]
    assert ack["resolved_at"] is not None  # resolved because the alert stopped firing

    position_data.by_symbol["AAPL"] = ASSIGNMENT  # ...and comes back
    assert _exits(client)["unacknowledged_critical"] == 1  # BR-098: needs a fresh acknowledgement
    assert _ack(client, t["trade_id"], "assignment_risk").status_code == 200
    assert client.get("/api/v1/alerts/acks", headers=ALICE).json()["total"] == 2


def test_closing_the_position_resolves_its_acknowledgement(
    client: TestClient, position_data
) -> None:
    t = _open(client, _portfolio(client))
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    _ack(client, t["trade_id"], "assignment_risk")
    client.post(
        f"/api/v1/trades/{t['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 12, "exit_date": TODAY()},
    )
    assert _exits(client)["alerts"] == []
    (ack,) = client.get("/api/v1/alerts/acks", headers=ALICE).json()["data"]
    assert ack["resolved_at"] is not None
    assert _ack(client, t["trade_id"], "assignment_risk").status_code == 404  # no longer active


def TODAY() -> str:  # noqa: N802 - small helper used inline above
    return date.today().isoformat()


# ------------------------------------------------- BR-011 in the entry gate


def _gate(client: TestClient, headers=ALICE) -> dict:
    return client.get("/api/v1/gate", headers=headers).json()["data"]


def test_with_no_open_positions_br011_is_checked_and_clear(client: TestClient) -> None:
    gate = _gate(client)
    assert (
        gate["clear"] is True
        and "BR-011" in gate["checked"]
        and "BR-011" not in gate["not_evaluated"]
    )


def test_an_assignment_alarm_blocks_new_entries_br011(client: TestClient, position_data) -> None:
    pid = _portfolio(client)
    _open(client, pid)
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    gate = _gate(client)
    assert gate["status"] == "BLOCKED" and "BR-011" in {r["rule_id"] for r in gate["reasons"]}

    r = client.post(
        "/api/v1/trades",
        headers=ALICE,
        json={
            "portfolio_id": pid,
            "symbol": "MSFT",
            "trade_type": "put",
            "direction": "short",
            "entry_price": 2,
            "quantity": 1,
            "entry_date": date.today().isoformat(),
            "layer": "base",
        },
    )
    assert r.status_code == 409
    assert "BR-011" in {x["rule_id"] for x in r.json()["error"]["details"]["reasons"]}


def test_unverifiable_alarms_are_reported_but_do_not_block(
    client: TestClient, position_data
) -> None:
    _open(client, _portfolio(client))
    position_data.unavailable = True
    gate = _gate(client)
    assert gate["clear"] is True and "BR-011" in gate["not_evaluated"]


# ------------------------------------------------------------------ picks


def _seed_picks() -> None:
    async def go() -> None:
        async with database.get_session() as s:
            this_week = date(2026, 6, 1)
            for sym, conf, wk in (
                ("AAPL", 0.61, this_week),
                ("MSFT", 0.88, this_week),
                ("TSLA", 0.40, this_week),
                ("OLD", 0.99, date(2026, 5, 25)),
            ):
                s.add(
                    m.WeeklyPick(
                        symbol=sym,
                        side="call",
                        strike=200,
                        expiry=date(2026, 7, 17),
                        entry_price=2.5,
                        target_price=4,
                        stop_loss=1.5,
                        rationale=f"{sym} momentum",
                        confidence=conf,
                        week_of=wk,
                    )
                )
            await s.commit()

    asyncio.run(go())


def test_picks_are_empty_until_the_weekly_job_has_run(client: TestClient) -> None:
    body = client.get("/api/v1/picks", headers=ALICE).json()
    assert body["data"] == [] and body["week_of"] is None


def test_latest_week_by_confidence_and_by_week(client: TestClient) -> None:
    _seed_picks()
    body = client.get("/api/v1/picks", headers=ALICE).json()
    assert body["week_of"] == "2026-06-01"
    assert [p["symbol"] for p in body["data"]] == ["MSFT", "AAPL", "TSLA"]  # best confidence first
    assert body["data"][0]["confidence"] == 0.88 and body["data"][0]["entry_price"] == 2.5
    older = client.get("/api/v1/picks?week_of=2026-05-25", headers=ALICE).json()
    assert [p["symbol"] for p in older["data"]] == ["OLD"]
    assert len(client.get("/api/v1/picks?limit=2", headers=ALICE).json()["data"]) == 2
    assert client.get("/api/v1/picks?limit=0", headers=ALICE).status_code == 422


def test_a_single_pick_and_a_missing_one(client: TestClient) -> None:
    _seed_picks()
    first = client.get("/api/v1/picks", headers=ALICE).json()["data"][0]
    one = client.get(f"/api/v1/picks/{first['id']}", headers=ALICE)
    assert one.status_code == 200 and one.json()["data"]["symbol"] == "MSFT"
    assert (
        client.get("/api/v1/picks/00000000-0000-0000-0000-000000000000", headers=ALICE).status_code
        == 404
    )


# -------------------------------------------------------------- dashboard


def _summary(client, headers=ALICE) -> dict:
    return client.get("/api/v1/dashboard/summary", headers=headers).json()["data"]


def test_an_empty_account_summary(client: TestClient) -> None:
    d = _summary(client)
    assert d["metrics"] == {
        "portfolio_value": 100000.0,
        "cash_available": 100000.0,
        "realized_pnl": 0.0,
        "unrealized_pnl": 0.0,
        "unrealized_complete": True,
        "open_trades": 0,
        "options_buying_power": 100000.0,
        "capital_at_risk": 0.0,
        "utilization_pct": 0.0,
        "account_size": 100000.0,
    }
    assert d["alerts"]["top"] == [] and d["holdings"] == [] and d["picks"]["top"] == []
    assert d["regime"]["state"] == "GROWTH" and d["regime"]["layer_split"] == {
        "base": 40,
        "growth": 60,
    }


def test_metrics_combine_realised_unrealised_and_capital_at_risk(client: TestClient) -> None:
    pid = _portfolio(client)
    closed = _open(client, pid, symbol="MSFT")  # short 1 @ 2.00, closed at 3.00 -> -$100
    client.post(
        f"/api/v1/trades/{closed['trade_id']}/close",
        headers=ALICE,
        json={"exit_price": 3.0, "exit_date": TODAY()},
    )
    _open(client, pid, risk_amount=5000)  # open: unrealised +$10 (2.00 -> 1.90)

    d = _summary(client)["metrics"]
    assert d["realized_pnl"] == -100.0 and d["unrealized_pnl"] == 10.0
    assert d["portfolio_value"] == 99910.0  # 100,000 - 100 + 10
    assert d["capital_at_risk"] == 5000.0
    assert d["options_buying_power"] == d["cash_available"] == 94900.0  # equity 99,900 - 5,000
    assert (
        d["utilization_pct"] == 5.0 and d["open_trades"] == 1 and d["unrealized_complete"] is True
    )


def test_unrealised_is_marked_incomplete_when_prices_are_missing(client, position_data) -> None:
    _open(client, _portfolio(client))
    position_data.unavailable = True
    m_ = _summary(client)["metrics"]
    assert (
        m_["unrealized_complete"] is False
        and m_["unrealized_pnl"] == 0.0
        and m_["open_trades"] == 1
    )


def test_the_summary_lists_top_alerts_holdings_and_picks(client: TestClient, position_data) -> None:
    pid = _portfolio(client)
    for sym in ("AAPL", "MSFT", "TSLA", "NVDA"):
        _open(client, pid, symbol=sym)
    position_data.by_symbol["AAPL"] = ASSIGNMENT
    position_data.by_symbol["MSFT"] = MarketInput(available=True, spot=200, mark=3.0, delta=-0.4)
    _seed_picks()
    d = _summary(client)
    assert d["alerts"]["summary"]["critical"] == 1 and d["alerts"]["unacknowledged_critical"] == 1
    assert [a["symbol"] for a in d["alerts"]["top"]] == ["AAPL", "MSFT"]  # only watch and above
    assert len(d["holdings"]) == 3 and d["holdings"][0]["symbol"] == "AAPL"
    assert d["picks"]["week_of"] == "2026-06-01" and d["picks"]["top"][0]["symbol"] == "MSFT"
    assert _summary(client, BOB)["metrics"]["open_trades"] == 0


def test_phase3_endpoints_require_authentication(client: TestClient) -> None:
    for method, path in (
        ("get", "/api/v1/alerts/exits"),
        ("post", "/api/v1/alerts/ack"),
        ("get", "/api/v1/alerts/acks"),
        ("get", "/api/v1/picks"),
        ("get", "/api/v1/dashboard/summary"),
    ):
        assert getattr(client, method)(path).status_code == 401, path

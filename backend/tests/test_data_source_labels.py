"""Responses must say whether data is live or a placeholder, and never cache fakes."""

from __future__ import annotations

import asyncio
import zlib

import httpx
import pytest
from fastapi.testclient import TestClient

from app.services import market, regime, screener

SCREENER_BODY = {
    "symbol": "AAPL",
    "expiry_days_min": 0,
    "expiry_days_max": 120,
    "min_volume": 0,
    "min_open_interest": 0,
    "limit": 5,
}


def _live_chain() -> list[dict]:
    from datetime import date, timedelta

    return [
        {
            "symbol": "AAPL",
            "strike": 200.0,
            "expiry": (date.today() + timedelta(days=30)).isoformat(),
            "option_type": "call",
            "bid": 1.0,
            "ask": 1.1,
            "last_price": 1.05,
            "implied_vol": 0.3,
            "delta": 0.5,
            "gamma": 0.01,
            "theta": -0.1,
            "vega": 0.2,
            "open_interest": 100,
            "volume": 10,
        }
    ]


# --- Screener ---------------------------------------------------------------


def test_screener_is_labelled_synthetic_when_yfinance_unavailable(
    client: TestClient, dev_headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(screener, "_get_spot_from_yfinance", lambda s: None)
    monkeypatch.setattr(screener, "_load_chain_from_yfinance", lambda s, spot, max_dte=90: None)
    r = client.post("/api/v1/screener/run", headers=dev_headers, json=SCREENER_BODY)
    assert r.status_code == 200, r.text
    assert r.json()["source"] == "synthetic"


def test_screener_is_labelled_live_only_when_spot_and_chain_are_live(
    client: TestClient, dev_headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(screener, "_get_spot_from_yfinance", lambda s: 201.0)
    monkeypatch.setattr(
        screener, "_load_chain_from_yfinance", lambda s, spot, max_dte=90: _live_chain()
    )
    r = client.post("/api/v1/screener/run", headers=dev_headers, json=SCREENER_BODY)
    assert r.json()["source"] == "live"

    # Live chain but placeholder spot => still not trustworthy.
    monkeypatch.setattr(screener, "_get_spot_from_yfinance", lambda s: None)
    r = client.post("/api/v1/screener/run", headers=dev_headers, json=SCREENER_BODY)
    assert r.json()["source"] == "synthetic"


def test_synthetic_data_is_stable_across_processes() -> None:
    # hash() of a str is randomized per process; crc32 is not.
    assert screener._stable_seed("AAPL") == zlib.crc32(b"AAPL")
    assert screener._load_chain_synthetic("XYZ", 100.0) == screener._load_chain_synthetic(
        "XYZ", 100.0
    )
    assert screener._get_fallback_spot("ZZZZ") == screener._get_fallback_spot("ZZZZ")


def test_synthetic_data_is_never_cached_to_supabase(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(screener, "_get_spot_from_yfinance", lambda s: None)

    def _boom(*a, **k):  # any HTTP call would mean we tried to write
        raise AssertionError("must not call Supabase when there is no live data")

    monkeypatch.setattr(screener.httpx, "AsyncClient", _boom)
    assert asyncio.run(screener.fetch_and_cache_supabase("AAPL", "http://x", "k")) is False

    monkeypatch.setattr(screener, "_get_spot_from_yfinance", lambda s: 200.0)
    monkeypatch.setattr(screener, "_load_chain_from_yfinance", lambda s, spot, max_dte=90: None)
    assert asyncio.run(screener.fetch_and_cache_supabase("AAPL", "http://x", "k")) is False


def test_live_chain_greeks_are_computed_not_zero() -> None:
    g = screener._chain_row_greeks(spot=100.0, strike=100.0, dte=30, iv=0.3, option_type="call")
    assert 0.4 < g["delta"] < 0.6
    assert g["gamma"] > 0 and g["vega"] > 0 and g["theta"] < 0


# --- Regime -----------------------------------------------------------------


def test_regime_source_label(
    client: TestClient, dev_headers, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(regime, "_fetch_vix_data", lambda: None)

    monkeypatch.setattr(regime, "_fetch_history_yfinance", lambda s, n: None)
    assert client.get("/api/v1/regime/SPY", headers=dev_headers).json()["source"] == "synthetic"

    monkeypatch.setattr(regime, "_fetch_history_yfinance", lambda s, n: [100.0, 101.0, 103.0])
    assert client.get("/api/v1/regime/SPY", headers=dev_headers).json()["source"] == "live"


# --- Market tickers ---------------------------------------------------------


def test_tickers_are_labelled_fallback_when_yahoo_fails(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def _fail(self, *a, **k):
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(market.httpx.AsyncClient, "get", _fail)
    body = client.get("/api/v1/market/tickers").json()
    assert body["source"] == "fallback"
    assert "SPY" in body["data"]

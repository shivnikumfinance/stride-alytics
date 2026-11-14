"""
Record the daily market regime score (0-100) and alert when its state changes.

Scheduled: Mon-Fri after the US close (see .github/workflows/generate-regime.yml).

Uses the same pure scoring code as the backend (backend/app/domain/regime_score.py) with the
DEFAULT weights, so the stored history is comparable day to day. Per-user weights are applied
live by the API and never stored here.

Never writes a made-up score: if SPY/VIX data cannot be fetched the job FAILS, which triggers the
existing failure notification in the reusable workflow.
"""

import os
import sys
from datetime import date

import httpx
from dotenv import load_dotenv

# Reuse the backend's pure scoring code (stdlib + yfinance only, no web/database imports).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from app.domain import regime_score as rs  # noqa: E402

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")


def _headers(prefer: str | None = None) -> dict[str, str]:
    headers = {
        "apikey": SUPABASE_KEY or "",
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def last_known_state() -> str | None:
    """State of the most recent stored row (today's if it exists, otherwise the previous day's)."""
    resp = httpx.get(
        f"{SUPABASE_URL}/rest/v1/market_regime",
        params={"select": "as_of,state", "order": "as_of.desc", "limit": "1"},
        headers=_headers(),
        timeout=15,
    )
    resp.raise_for_status()
    rows = resp.json()
    return rows[0]["state"] if rows else None


def store(regime: rs.RegimeScore) -> None:
    resp = httpx.post(
        f"{SUPABASE_URL}/rest/v1/market_regime",
        params={"on_conflict": "as_of"},
        headers=_headers("resolution=merge-duplicates"),
        json=regime.to_row(),
        timeout=15,
    )
    resp.raise_for_status()


def alert(message: str) -> None:
    if not SLACK_WEBHOOK:
        print(f"[alert not sent: SLACK_WEBHOOK unset] {message}")
        return
    try:
        httpx.post(SLACK_WEBHOOK, json={"text": message}, timeout=10)
    except Exception as exc:  # alerting must never fail the job
        print(f"[alert failed] {exc}")


def main() -> int:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("SUPABASE_URL and SUPABASE_KEY are required", file=sys.stderr)
        return 1

    regime = rs.compute_live()
    if regime.score is None:
        print("Could not compute the regime score (SPY/VIX data unavailable).", file=sys.stderr)
        return 1

    previous = last_known_state()
    store(regime)
    print(
        f"{date.today()} regime score {regime.score} -> {regime.state} "
        f"(vix={regime.vix}, iv_rank={regime.iv_rank}, market_down={regime.market_down}, "
        f"missing={regime.missing or 'none'})"
    )

    if previous and previous != regime.state:
        alert(f"Market regime changed: {previous} -> {regime.state} (score {regime.score}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

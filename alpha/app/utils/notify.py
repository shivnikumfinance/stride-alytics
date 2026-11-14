"""Failure/warning alerts via the optional Slack and Discord webhooks.

``send_alert`` never raises: alerting must not turn a warning into a crash.
"""

from __future__ import annotations

import requests

from app.config import config

_TIMEOUT_SECONDS = 10


def send_alert(message: str) -> bool:
    """Post ``message`` to every configured webhook. Returns True if any accepted it."""
    delivered = False
    targets = (
        (config.SLACK_WEBHOOK_URL, "text"),
        (config.DISCORD_WEBHOOK_URL, "content"),
    )
    for url, field in targets:
        if not url:
            continue
        try:
            resp = requests.post(url, json={field: message[:1900]}, timeout=_TIMEOUT_SECONDS)
            if resp.ok:
                delivered = True
            else:
                print(f"[WARNING] Alert webhook returned HTTP {resp.status_code}")
        except Exception as exc:  # noqa: BLE001 - alerting must never raise
            print(f"[WARNING] Could not send alert: {exc}")
    if not delivered:
        print(f"[ALERT - not delivered] {message}")
    return delivered

"""
Push DataFrames to Google Sheets using the Sheets REST API (requests library).
"""
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_creds():
    """Get Google service account credentials."""
    val = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if val:
        return Credentials.from_service_account_info(json.loads(val), scopes=SCOPES)
    for p in ["service_account.json", "../service_account.json"]:
        if os.path.exists(p):
            return Credentials.from_service_account_file(p, scopes=SCOPES)
    raise FileNotFoundError(
        "No Google service account credentials found. "
        "Set GOOGLE_SERVICE_ACCOUNT_JSON env var or place service_account.json."
    )


def _api(method: str, url: str, body: dict | None = None) -> dict:
    """Authenticated Google Sheets API call using requests library."""
    creds = _get_creds()
    creds.refresh(Request())
    headers = {"Authorization": "Bearer " + creds.token, "Content-Type": "application/json"}
    r = requests.request(method, url, json=body, headers=headers, timeout=20)
    if not r.ok:
        raise RuntimeError(f"Google API error {r.status_code}: {r.text[:300]}")
    return r.json()


import urllib.parse


def _ensure_worksheet(sid: str, name: str) -> None:
    """Create worksheet if it doesn't exist."""
    try:
        _api("GET", f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=sheets.properties")
    except Exception:
        pass
    try:
        _api(
            "POST",
            f"https://sheets.googleapis.com/v4/spreadsheets/{sid}:batchUpdate",
            {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": name,
                                "gridProperties": {"rowCount": 500, "columnCount": 26},
                            }
                        }
                    }
                ]
            },
        )
    except RuntimeError as e:
        if "409" not in str(e) and "already exists" not in str(e).lower():
            raise  # re-raise unexpected errors


def push_to_sheet(df: pd.DataFrame, sheet_name: str) -> None:
    """
    Push a DataFrame to a specific worksheet.
    Requires GOOGLE_SHEETS_SPREADSHEET_ID in .env or env.
    The spreadsheet must already exist and be shared with the service account email.
    """
    sid = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
    if not sid:
        raise RuntimeError(
            "GOOGLE_SHEETS_SPREADSHEET_ID is not set. "
            "Add it to alpha/.env or set it as an environment variable."
        )

    # Ensure the worksheet exists
    _ensure_worksheet(sid, sheet_name)

    # URL-encode sheet name for API calls
    encoded_name = urllib.parse.quote(sheet_name)

    # Clear existing data
    try:
        _api("POST", f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{encoded_name}!A1:Z500:clear", {})
    except Exception:
        pass

    # Write data — convert all values to strings to handle Timestamps, dates, etc.
    values = [df.columns.values.tolist()] + df.astype(str).values.tolist()
    _api(
        "PUT",
        f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{encoded_name}!A1:Z{len(values)}?valueInputOption=USER_ENTERED",
        {"values": values},
    )
    print(f"[GSHEETS] Pushed {len(df)} rows to '{sheet_name}'")

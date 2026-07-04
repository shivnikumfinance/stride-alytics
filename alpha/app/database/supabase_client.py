"""
Alpha Option Trading System — Supabase Client

This module initializes a Supabase client using:
- SUPABASE_URL
- SUPABASE_KEY (service_role)

It exposes a single function:
    get_supabase_client()

All other modules (ingest.py, main.py, streamlit_app.py)
should import this function to interact with Supabase.
"""

from supabase import create_client, Client
from app.config import config


# ─────────────────────────────────────────────
# Validate Environment Variables
# ─────────────────────────────────────────────


def _validate_supabase_env():
    if not config.SUPABASE_URL:
        raise ValueError("[ERROR] SUPABASE_URL is missing. Add it to your .env file.")

    if not config.SUPABASE_KEY:
        raise ValueError(
            "[ERROR] SUPABASE_KEY (service_role) is missing. Add it to your .env file."
        )


# ─────────────────────────────────────────────
# Create Supabase Client
# ─────────────────────────────────────────────

_supabase_client: Client | None = None


def get_supabase_client() -> Client:
    """
    Returns a singleton Supabase client.
    Ensures the client is created only once.
    """

    global _supabase_client

    if _supabase_client is None:
        _validate_supabase_env()

        _supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

        print("[INFO] Supabase client initialized")

    return _supabase_client


# ─────────────────────────────────────────────
# Helper CRUD Wrappers (Optional)
# ─────────────────────────────────────────────


def insert_rows(table: str, rows: list[dict]):
    """Insert multiple rows into a Supabase table."""
    client = get_supabase_client()
    return client.table(table).insert(rows).execute()


def delete_rows(table: str, column: str, value):
    """Delete rows where column == value."""
    client = get_supabase_client()
    return client.table(table).delete().eq(column, value).execute()


def fetch_all(table: str):
    """Fetch all rows from a table."""
    client = get_supabase_client()
    resp = client.table(table).select("*").execute()
    return resp.data


def fetch_filtered(table: str, column: str, value):
    """Fetch rows where column == value."""
    client = get_supabase_client()
    resp = client.table(table).select("*").eq(column, value).execute()
    return resp.data


# ─────────────────────────────────────────────
# Manual Test Harness
# ─────────────────────────────────────────────

if __name__ == "__main__":
    client = get_supabase_client()

    print("\n[INFO] Testing Supabase connection...")
    try:
        resp = client.table("audit_log").select("*").limit(5).execute()
        print("[OK] Connection OK — audit_log sample:")
        print(resp.data)
    except Exception as e:
        print("[ERROR] Supabase error:", e)

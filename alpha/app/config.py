"""
Alpha Option Trading System — Config Loader
Loads environment variables and exposes them as a typed config object.
"""

from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file
load_dotenv()


@dataclass
class Config:
    # Supabase
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    # APIs
    POLYGON_API_KEY: str | None = None
    FMP_API_KEY: str | None = None
    MASSIVE_API_KEY: str | None = None

    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_JSON: str | None = None
    GOOGLE_SHEETS_SPREADSHEET_ID: str | None = None

    # Optional integrations
    SLACK_WEBHOOK_URL: str | None = None
    DISCORD_WEBHOOK_URL: str | None = None

    # Internal API token (optional)
    API_AUTH_TOKEN: str | None = None


config = Config(
    SUPABASE_URL=__import__("os").getenv("SUPABASE_URL"),
    SUPABASE_KEY=__import__("os").getenv("SUPABASE_KEY"),
    POLYGON_API_KEY=__import__("os").getenv("POLYGON_API_KEY"),
    FMP_API_KEY=__import__("os").getenv("FMP_API_KEY"),
    MASSIVE_API_KEY=__import__("os").getenv("MASSIVE_API_KEY"),
    GOOGLE_SERVICE_ACCOUNT_JSON=__import__("os").getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
    GOOGLE_SHEETS_SPREADSHEET_ID=__import__("os").getenv("GOOGLE_SHEETS_SPREADSHEET_ID"),
    SLACK_WEBHOOK_URL=__import__("os").getenv("SLACK_WEBHOOK_URL"),
    DISCORD_WEBHOOK_URL=__import__("os").getenv("DISCORD_WEBHOOK_URL"),
    API_AUTH_TOKEN=__import__("os").getenv("API_AUTH_TOKEN"),
)

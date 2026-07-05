"""
Alpha Option Trading System — Secrets Validator
Ensures all required API keys are present before running the engine.
"""

from app.config import config

REQUIRED_KEYS = {
    "SUPABASE_URL": config.SUPABASE_URL,
    "SUPABASE_KEY": config.SUPABASE_KEY,
    "POLYGON_API_KEY": config.POLYGON_API_KEY,
    "FMP_API_KEY": config.FMP_API_KEY,
}

OPTIONAL_KEYS = {
    "MASSIVE_API_KEY": config.MASSIVE_API_KEY,
    "GOOGLE_SERVICE_ACCOUNT_JSON": config.GOOGLE_SERVICE_ACCOUNT_JSON,
    "GOOGLE_SHEETS_SPREADSHEET_ID": config.GOOGLE_SHEETS_SPREADSHEET_ID,
    "SLACK_WEBHOOK_URL": config.SLACK_WEBHOOK_URL,
    "DISCORD_WEBHOOK_URL": config.DISCORD_WEBHOOK_URL,
    "API_AUTH_TOKEN": config.API_AUTH_TOKEN,
}


def validate_required_keys():
    missing = [key for key, value in REQUIRED_KEYS.items() if not value]
    if missing:
        print("\n[ERROR] Missing required environment variables:")
        for key in missing:
            print(f"   - {key}")
        print("\nFix your .env file before running Alpha.\n")
        raise SystemExit(1)

    print("\n[OK] All required environment variables are present.\n")


def show_optional_keys():
    print("[INFO] Optional keys:")
    for key, value in OPTIONAL_KEYS.items():
        status = "Loaded" if value else "Not set"
        print(f"   {key}: {status}")


if __name__ == "__main__":
    validate_required_keys()
    show_optional_keys()

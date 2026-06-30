"""Pydantic-based settings using environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    APP_NAME: str = "StrideAlytics"
    DEBUG: bool = False

    # --- Database (Supabase / PostgreSQL) ---
    DATABASE_URL: str | None = None
    DATABASE_POOL_SIZE: int = 5

    # --- Auth (Supabase) ---
    SUPABASE_URL: str | None = None
    SUPABASE_ANON_KEY: str | None = None
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    SUPABASE_JWT_SECRET: str | None = None

    # --- Email ---
    SENDGRID_API_KEY: str | None = None

    # --- Notifications ---
    SLACK_WEBHOOK: str | None = None

    # --- App ---
    ENVIRONMENT: str = "development"

    # --- CORS ---
    CORS_ORIGINS: str = "*"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

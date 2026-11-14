"""ORM model for per-user settings (table created in migration 005, extended in 007)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DECIMAL, Boolean, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models._types import JSONType, utcnow

# Business-rule defaults (docs: BR-030, BR-034, FR-650/660, regime inputs).
DEFAULT_BAND_CAPS: dict[str, float] = {"A": 30, "B": 25, "C": 20, "D": 15, "E": 10}
DEFAULT_REGIME_WEIGHTS: dict[str, float] = {"trend": 40, "vix": 30, "iv_rank": 30}


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    notify_weekly_picks: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_market_regime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_symbol: Mapped[str] = mapped_column(String, default="SPY", nullable=False)
    theme: Mapped[str] = mapped_column(String, default="light", nullable=False)
    screener_preset: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)

    # --- Added in migration 007 ---
    account_size: Mapped[float] = mapped_column(DECIMAL(14, 2), default=100000, nullable=False)
    base_risk_pct: Mapped[float] = mapped_column(DECIMAL(5, 2), default=1.25, nullable=False)
    growth_risk_pct: Mapped[float] = mapped_column(DECIMAL(5, 2), default=2.5, nullable=False)
    min_equity: Mapped[float] = mapped_column(DECIMAL(14, 2), default=0, nullable=False)
    band_caps: Mapped[dict[str, Any]] = mapped_column(
        JSONType, default=lambda: dict(DEFAULT_BAND_CAPS), nullable=False
    )
    regime_weights: Mapped[dict[str, Any]] = mapped_column(
        JSONType, default=lambda: dict(DEFAULT_REGIME_WEIGHTS), nullable=False
    )
    widget_toggles: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    disclaimer_accepted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    enforce_gate: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utcnow, server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=utcnow,
        server_default=text("now()"),
        onupdate=utcnow,
        nullable=False,
    )

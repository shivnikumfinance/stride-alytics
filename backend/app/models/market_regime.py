"""ORM model for the shared daily regime score (migration 008)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import DECIMAL, Boolean, Date, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models._types import JSONType, utcnow


class MarketRegime(Base):
    __tablename__ = "market_regime"

    as_of: Mapped[date] = mapped_column(Date, primary_key=True)
    score: Mapped[float | None] = mapped_column(DECIMAL(5, 1), nullable=True)
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    components: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    weights: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    vix: Mapped[float | None] = mapped_column(DECIMAL(6, 2), nullable=True)
    iv_rank: Mapped[float | None] = mapped_column(DECIMAL(5, 1), nullable=True)
    market_down: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    source: Mapped[str] = mapped_column(String(16), default="live", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utcnow, server_default=text("now()"), nullable=False
    )

"""SQLAlchemy ORM model for trades."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DECIMAL, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Trade(Base):
    """Single options or stock trade."""

    __tablename__ = "trades"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    portfolio_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(nullable=False)
    trade_type: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
    entry_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    exit_price: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    entry_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    exit_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False
    )

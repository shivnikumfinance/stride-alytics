"""SQLAlchemy ORM model for trades."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DECIMAL, Date, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models._types import new_uuid, utcnow

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio


class Trade(Base):
    """Single options or stock trade."""

    __tablename__ = "trades"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=new_uuid, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    portfolio_id: Mapped[UUID] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False, index=True
    )
    symbol: Mapped[str] = mapped_column(nullable=False)
    trade_type: Mapped[str] = mapped_column(nullable=False)
    direction: Mapped[str] = mapped_column(nullable=False)
    entry_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    exit_price: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    entry_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    exit_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(nullable=True)

    # --- Fields added in migration 007 (needed for DTE, Greeks, risk and band caps) ---
    strike: Mapped[float | None] = mapped_column(DECIMAL(10, 2), nullable=True)
    expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    strategy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    layer: Mapped[str | None] = mapped_column(String(8), nullable=True)  # 'base' | 'growth'
    band: Mapped[str | None] = mapped_column(String(1), nullable=True)  # 'A'..'E'
    risk_amount: Mapped[float | None] = mapped_column(DECIMAL(12, 2), nullable=True)
    credit: Mapped[float | None] = mapped_column(DECIMAL(10, 4), nullable=True)

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

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="trades")

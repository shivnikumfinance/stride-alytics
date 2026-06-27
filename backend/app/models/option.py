"""SQLAlchemy ORM model for options chains."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Date, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Option(Base):
    """Option chain snapshot (one row per contract)."""

    __tablename__ = "options"

    symbol: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    strike: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), primary_key=True, nullable=False)
    expiry: Mapped[datetime] = mapped_column(Date, primary_key=True, nullable=False)
    option_type: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    bid: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4), nullable=True)
    ask: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4), nullable=True)
    last_price: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 4), nullable=True)
    implied_vol: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 4), nullable=True)
    delta: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 4), nullable=True)
    gamma: Mapped[Decimal | None] = mapped_column(DECIMAL(7, 6), nullable=True)
    theta: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 4), nullable=True)
    vega: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 4), nullable=True)
    rho: Mapped[Decimal | None] = mapped_column(DECIMAL(5, 4), nullable=True)
    open_interest: Mapped[int | None] = mapped_column(nullable=True)
    volume: Mapped[int | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
"""SQLAlchemy ORM model for portfolios."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Portfolio(Base):
    """User portfolio container."""

    __tablename__ = "portfolios"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False
    )

    trades: Mapped[list["Trade"]] = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")

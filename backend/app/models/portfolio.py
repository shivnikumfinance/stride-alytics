"""SQLAlchemy ORM model for portfolios."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models._types import new_uuid, utcnow

if TYPE_CHECKING:
    from app.models.trade import Trade


class Portfolio(Base):
    """User portfolio container."""

    __tablename__ = "portfolios"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_portfolio_user_name"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=new_uuid, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
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

    trades: Mapped[list["Trade"]] = relationship(
        "Trade", back_populates="portfolio", cascade="all, delete-orphan"
    )

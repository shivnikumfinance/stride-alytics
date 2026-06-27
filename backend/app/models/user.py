"""SQLAlchemy ORM model for users."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """Supabase-aligned user profile."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("auth.uid()"))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    subscription_plan: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'free'")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False
    )
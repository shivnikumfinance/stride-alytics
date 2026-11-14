"""ORM model for saved scenarios (migration 010)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, String, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models._types import JSONType, new_uuid, utcnow


class Scenario(Base):
    __tablename__ = "scenarios"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_scenarios_user_name"),)

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=new_uuid, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utcnow, server_default=text("now()"), nullable=False
    )

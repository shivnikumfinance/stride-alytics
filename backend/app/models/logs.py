"""Append-only decision/audit logs (BR-060–064).

Rows can be inserted and read but never changed or deleted. Two layers enforce it:
* PostgreSQL: a trigger in migration 007 raises on UPDATE/DELETE.
* Application: the ``before_flush`` guard below rejects it for every database.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import String, TIMESTAMP, Text, event, text
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.database import Base
from app.models._types import JSONType, new_uuid, utcnow


class ImmutableRecordError(RuntimeError):
    """Raised when code tries to modify or delete an append-only log row."""


class SignalLog(Base):
    """A rule/gate decision, including blocked signals (BR-061)."""

    __tablename__ = "signal_log"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=new_uuid, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utcnow, server_default=text("now()"), nullable=False
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # gate | regime | alert | ...
    symbol: Mapped[str | None] = mapped_column(String(16), nullable=True)
    rule_id: Mapped[str | None] = mapped_column(String(16), nullable=True)  # e.g. BR-017
    decision: Mapped[str] = mapped_column(String(16), nullable=False)  # allowed | blocked | info
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONType, default=dict, nullable=False)


class AuditLog(Base):
    """A user-visible change: who did what to which record (BR-060/062)."""

    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=new_uuid, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=utcnow, server_default=text("now()"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # trade.add, settings.update...
    entity: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONType, nullable=True)


_IMMUTABLE = (SignalLog, AuditLog)


@event.listens_for(Session, "before_flush")
def _guard_append_only(session: Session, flush_context: object, instances: object) -> None:
    for obj in session.deleted:
        if isinstance(obj, _IMMUTABLE):
            raise ImmutableRecordError(f"{type(obj).__name__} rows cannot be deleted")
    for obj in session.dirty:
        if isinstance(obj, _IMMUTABLE) and session.is_modified(obj):
            raise ImmutableRecordError(f"{type(obj).__name__} rows cannot be modified")

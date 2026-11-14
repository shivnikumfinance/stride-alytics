"""Shared column helpers for the ORM models."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# JSONB on PostgreSQL, plain JSON elsewhere (SQLite in dev/tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    """Timezone-aware 'now' used as the Python-side default for timestamps."""
    return datetime.now(timezone.utc)


def new_uuid() -> UUID:
    """Python-side default for primary keys (works on SQLite and PostgreSQL)."""
    return uuid4()

"""FastAPI dependencies shared by the v1 endpoints."""

from __future__ import annotations

import csv
import io
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends

from app.api.middleware.auth import CurrentUser, get_current_user
from app.database import get_session
from app.repositories.sql import Repo


def resolve_user_uuid(raw: str) -> UUID:
    """Supabase ids are UUIDs; dev tokens use arbitrary strings, mapped deterministically."""
    try:
        return UUID(raw)
    except (ValueError, AttributeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, raw)


@dataclass
class Ctx:
    """The authenticated user plus a repository bound to this request's session."""

    user_id: UUID
    email: str | None
    repo: Repo


async def get_repo() -> AsyncIterator[Repo]:
    async with get_session() as session:
        yield Repo(session)


async def get_ctx(
    current_user: CurrentUser = Depends(get_current_user),
    repo: Repo = Depends(get_repo),
) -> Ctx:
    user_id = resolve_user_uuid(current_user.user_id)
    await repo.ensure_user(user_id, current_user.email)
    return Ctx(user_id=user_id, email=current_user.email, repo=repo)


def csv_safe(value: object) -> object:
    """Neutralise spreadsheet formula injection in exported text cells."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def to_csv(columns: list[str], rows: list[dict]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(columns)
    for row in rows:
        writer.writerow([csv_safe(row.get(c)) for c in columns])
    return buf.getvalue()

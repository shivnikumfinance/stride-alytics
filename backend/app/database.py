"""Database engine, sessions and schema helpers.

Production uses PostgreSQL (``DATABASE_URL``, Supabase). When no URL is set the
app falls back to an **in-memory SQLite** database so local development and
tests need no Postgres; that data is lost on restart, and a warning is logged.
There is one code path (SQLAlchemy) for both.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.config import settings

logger = logging.getLogger(__name__)

SQLITE_MEMORY_URL = "sqlite+aiosqlite:///:memory:"


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None
using_sqlite_fallback: bool = False


def normalize_url(url: str) -> str:
    """Use the psycopg driver for plain postgresql:// URLs."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def configure_engine(url: str) -> None:
    """(Re)create the global engine and session factory for ``url``."""
    global engine, async_session_factory, using_sqlite_fallback
    url = normalize_url(url)
    kwargs: dict = {"echo": settings.DEBUG}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url:
            kwargs["poolclass"] = StaticPool  # keep one connection so the DB survives
    else:
        kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    engine = create_async_engine(url, **kwargs)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    using_sqlite_fallback = url.startswith("sqlite")


def sanitize_for_sqlite(metadata: MetaData) -> None:
    """Drop Postgres-only server defaults so the schema can be created on SQLite.

    Python-side ``default=`` values on the models fill ids and timestamps, so
    nothing is lost. **Mutates ``metadata`` for the whole process** — only call
    it when the database really is SQLite (dev fallback and tests).
    """
    for table in metadata.tables.values():
        for column in table.columns:
            if column.server_default is not None:
                text_value = str(column.server_default.arg)
                if any(t in text_value for t in ("auth.uid()", "gen_random_uuid()", "now()")):
                    column.server_default = None
            if column.server_onupdate is not None and "now()" in str(column.server_onupdate.arg):
                column.server_onupdate = None
            if column.onupdate is not None:
                arg = getattr(column.onupdate, "arg", column.onupdate)
                if "now()" in str(arg):
                    column.onupdate = None


async def init_db() -> None:
    """Pick the engine on startup; create the schema when using the SQLite fallback."""
    if engine is None:
        if settings.DATABASE_URL:
            configure_engine(settings.DATABASE_URL)
        else:
            configure_engine(SQLITE_MEMORY_URL)
            logger.warning(
                "DATABASE_URL is not set: using an in-memory SQLite database. "
                "All data is lost when the process restarts."
            )
    if using_sqlite_fallback:
        import app.models  # noqa: F401  (registers every model on Base.metadata)

        sanitize_for_sqlite(Base.metadata)
        assert engine is not None
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def verify_db_connection() -> bool:
    """Ping the database and log the result."""
    if engine is None:
        logger.warning("No database engine configured — skipping DB connectivity check.")
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified.")
        return True
    except Exception as exc:
        logger.error("Database connection failed: %s", exc)
        return False


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session (use with ``async with``)."""
    if async_session_factory is None:
        raise RuntimeError("Database is not initialised (init_db was not called).")
    async with async_session_factory() as session:
        yield session

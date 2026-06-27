"""Database connection verification using psycopg / SQLAlchemy."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

engine = None
async_session_factory = None

if settings.DATABASE_URL:
    # Convert standard postgresql:// to psycopg postgresql+psycopg://
    dsns = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_async_engine(dsns, pool_size=settings.DATABASE_POOL_SIZE, echo=settings.DEBUG)
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def verify_db_connection() -> bool:
    """Ping the database and log the result."""
    if engine is None:
        logger.warning("DATABASE_URL not set — skipping DB connectivity check.")
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        logger.info("✓ Database connection verified.")
        return True
    except Exception as exc:
        logger.error("✗ Database connection failed: %s", exc)
        return False


async def get_session() -> AsyncSession:  # type: ignore[return]
    """Yield an async database session (for dependency injection)."""
    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL is not configured.")
    async with async_session_factory() as session:
        yield session
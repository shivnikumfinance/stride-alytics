"""StrideAlytics Backend — FastAPI entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.error_handler import install_exception_handlers
from app.api.middleware.logging import AccessLogMiddleware
from app.api.v1.router import router as api_v1_router
from app.config import settings
from app.database import init_db, verify_db_connection
from app.utils.logger import configure_logging, get_logger

configure_logging(level="DEBUG" if settings.DEBUG else "INFO")
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Verify connectivity on boot; nothing else to clean up."""
    log.info("app.startup", app=settings.APP_NAME, debug=settings.DEBUG)
    await init_db()  # Postgres via DATABASE_URL, else an in-memory SQLite fallback
    if settings.DATABASE_URL:
        await verify_db_connection()
    yield
    log.info("app.shutdown")


app = FastAPI(
    title="StrideAlytics API",
    version="0.1.0",
    description="Options trading analytics — multi-platform (web/mobile/API).",
    lifespan=lifespan,
)

# --- Middleware (order matters: outermost first) ---
app.add_middleware(AccessLogMiddleware)
# Auth uses a bearer header, not cookies, so credentials are only allowed for explicit origins
# (browsers reject "*" together with credentials). Set CORS_ORIGINS to the frontend URL in production.
_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()] or ["*"]
if "*" in _origins and settings.ENVIRONMENT != "development":
    log.warning("cors.wildcard_origin", hint="set CORS_ORIGINS to your frontend URL")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials="*" not in _origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_exception_handlers(app)

# --- Routers ---
app.include_router(api_v1_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, Any]:
    """Liveness probe for the platform health check (also at ``/api/v1/health``)."""
    return {"success": True, "data": {"status": "ok"}}


@app.get("/", tags=["root"])
async def root() -> dict[str, Any]:
    """Root discovery endpoint."""
    return {
        "success": True,
        "data": {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "docs": "/docs",
            "api": "/api/v1",
        },
    }

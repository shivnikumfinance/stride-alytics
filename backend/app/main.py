"""StrideAlytics Backend — FastAPI entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.error_handler import install_exception_handlers
from app.api.middleware.logging import AccessLogMiddleware
from app.api.v1.router import router as api_v1_router
from app.config import settings
from app.database import verify_db_connection
from app.utils.logger import configure_logging, get_logger

configure_logging(level="DEBUG" if settings.DEBUG else "INFO")
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify connectivity on boot; nothing else to clean up."""
    log.info("app.startup", app=settings.APP_NAME, debug=settings.DEBUG)
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_exception_handlers(app)

# --- Routers ---
app.include_router(api_v1_router)


@app.get("/", tags=["root"])
async def root() -> dict:
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
"""Custom FastAPI middleware (auth, logging, error handling)."""

from app.api.middleware.auth import (
    CurrentUser,
    get_current_user,
    get_optional_user,
    verify_jwt,
    verify_optional_user,
)
from app.api.middleware.error_handler import install_exception_handlers
from app.api.middleware.logging import AccessLogMiddleware

__all__ = [
    "CurrentUser",
    "get_current_user",
    "get_optional_user",
    "verify_jwt",
    "verify_optional_user",
    "install_exception_handlers",
    "AccessLogMiddleware",
]

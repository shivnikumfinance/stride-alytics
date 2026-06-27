"""Per-request structured access logging."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.logger import get_logger

log = get_logger(__name__)


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Emit a single structured log line for every HTTP request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        log.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
            client=request.client.host if request.client else None,
        )
        return response

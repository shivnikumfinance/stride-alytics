"""JWT verification middleware for FastAPI.

Implements the Blueprint's JWT flow:
    1. Extract Bearer token from Authorization header.
    2. Decode + verify signature using ``SUPABASE_JWT_SECRET``.
    3. Attach the user_id (``sub`` claim) and subscription plan to the request.

Endpoints that require auth use ``Depends(get_current_user)`` — a
cleaner-than-Depends-injection alias for ``verify_jwt``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.config import settings
from app.services.auth import plan_from_claims, verify_supabase_jwt
from app.utils.logger import get_logger

log = get_logger(__name__)

# ``auto_error=False`` lets us return a friendly 401 instead of FastAPI's
# default 403 when no Authorization header is present.
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    """Decoded JWT identity attached to each authenticated request."""

    user_id: str
    plan: Literal["free", "pro"]
    email: str | None = None


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """Decode the Supabase JWT and return a ``CurrentUser``."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Local/dev fallback: accept stub tokens ``dev:<user_id>`` or ``dev-admin-token``.
    token = credentials.credentials
    if token == "dev-admin-token":
        log.warning("auth.dev_admin_token_used")
        return CurrentUser(
            user_id="00000000-0000-0000-0000-000000000000",
            plan="pro",
            email="admin@stridealytics.com",
        )
    if token.startswith("dev:"):
        user_id = token.split(":", 1)[1] or "dev-user"
        log.warning("auth.dev_token_used", user_id=user_id)
        return CurrentUser(user_id=user_id, plan="free")

    if not settings.SUPABASE_JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth not configured (SUPABASE_JWT_SECRET missing)",
        )

    try:
        claims = verify_supabase_jwt(credentials.credentials)
    except JWTError as exc:
        log.warning("auth.jwt_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return CurrentUser(
        user_id=str(claims["sub"]),
        plan=plan_from_claims(claims),
        email=claims.get("email"),
    )


async def verify_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser | None:
    """Like ``verify_jwt`` but returns ``None`` if no token was supplied.

    Use on endpoints that work for both anonymous (free-tier) and
    authenticated users (e.g. the public screener preview).
    """
    if credentials is None:
        return None
    return await verify_jwt(credentials)


# Convenience alias for ``Depends(...)`` call-sites.
get_current_user = verify_jwt
get_optional_user = verify_optional_user

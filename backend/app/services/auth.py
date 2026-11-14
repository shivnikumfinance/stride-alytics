"""Auth helpers.

Phase 1 keeps the logic minimal so the endpoint contract works against
a Supabase JWT verifier. The actual Supabase REST call lives in
``supabase_client`` (added in Phase 2 when ``SUPABASE_URL`` is set).
"""

from __future__ import annotations

from typing import Any

from jose import JWTError, jwt

from app.config import settings
from app.utils.logger import get_logger

log = get_logger(__name__)

JWT_ALGORITHM = "HS256"


def dev_auth_enabled() -> bool:
    """True only when running with ``ENVIRONMENT=development``.

    Gates the stub tokens (``dev:<id>``, ``dev-admin-token``) and the dev
    login fallback so they can never be used against a deployed API.
    """
    return settings.ENVIRONMENT.strip().lower() == "development"


def get_jwt_secret() -> str:
    # Read from settings (which also loads .env), not os.getenv, so the value
    # the middleware checked is the value used here.
    secret = settings.SUPABASE_JWT_SECRET
    if not secret:
        raise RuntimeError("SUPABASE_JWT_SECRET is not configured")
    return secret


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Decode a Supabase-issued JWT and return its claims.

    Supabase access tokens carry ``aud: "authenticated"``; python-jose rejects
    any token with an ``aud`` claim unless the expected audience is passed.

    Raises ``JWTError`` on invalid/expired tokens.
    """
    secret = get_jwt_secret()
    claims = jwt.decode(
        token,
        secret,
        algorithms=[JWT_ALGORITHM],
        audience=settings.SUPABASE_JWT_AUDIENCE,
    )
    if "sub" not in claims:
        raise JWTError("missing 'sub' claim in JWT")
    return claims

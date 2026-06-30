"""Auth helpers.

Phase 1 keeps the logic minimal so the endpoint contract works against
a Supabase JWT verifier. The actual Supabase REST call lives in
``supabase_client`` (added in Phase 2 when ``SUPABASE_URL`` is set).
"""

from __future__ import annotations

import os
from typing import Any, Literal

from jose import JWTError, jwt

from app.utils.logger import get_logger

log = get_logger(__name__)

JWT_ALGORITHM = "HS256"


def get_jwt_secret() -> str:
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        raise RuntimeError("SUPABASE_JWT_SECRET is not configured")
    return secret


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Decode a Supabase-issued JWT and return its claims.

    Raises ``JWTError`` on invalid/expired tokens.
    """
    secret = get_jwt_secret()
    claims = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    if "sub" not in claims:
        raise JWTError("missing 'sub' claim in JWT")
    return claims


def plan_from_claims(claims: dict[str, Any]) -> Literal["free", "pro"]:
    """Map a Supabase user_metadata blob to a subscription plan."""
    meta = claims.get("user_metadata") or {}
    plan = (meta.get("subscription_plan") or "free").lower()
    return "pro" if plan == "pro" else "free"

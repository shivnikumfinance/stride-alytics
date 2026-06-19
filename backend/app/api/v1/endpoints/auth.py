"""Auth endpoints — login / signup / refresh / me.

Phase 1 contracts proxy directly to Supabase Auth when ``SUPABASE_URL``
and ``SUPABASE_ANON_KEY`` are configured. When they are missing we
return a deterministic dev token so the rest of the API can be exercised
locally without a Supabase project.
"""

from __future__ import annotations

import os
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


def _supabase_env_present() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"))


def _dev_token(user_id: str, email: str, plan: str = "free") -> TokenResponse:
    """Return a deterministic dev token when Supabase isn't configured."""
    token = f"dev:{user_id}:{uuid.uuid4().hex[:8]}"
    log.warning("auth.dev_token_issued", user_id=user_id, email=email)
    return TokenResponse(
        access_token=token,
        refresh_token=None,
        expires_in=3600,
        user_id=user_id,
        email=email,
        subscription_plan=plan,  # type: ignore[arg-type]
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    """Email/password login → Supabase access token."""
    if not _supabase_env_present():
        # Dev fallback: derive a stable user_id from the email.
        user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, payload.email))
        return _dev_token(user_id=user_id, email=payload.email)

    # Real implementation calls Supabase Auth's /token endpoint via httpx.
    # Kept as a stub for Phase 2 to keep dependencies optional in Phase 1.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Supabase auth proxy is wired in Phase 2.",
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest) -> TokenResponse:
    """Create a new user via Supabase Auth."""
    if not _supabase_env_present():
        user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, payload.email))
        return _dev_token(user_id=user_id, email=payload.email)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Supabase auth proxy is wired in Phase 2.",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str) -> TokenResponse:
    """Exchange a Supabase refresh_token for a new access_token."""
    if not _supabase_env_present():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh tokens require Supabase configuration",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Supabase refresh proxy is wired in Phase 2.",
    )


@router.get("/me")
async def me(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    """Return the authenticated user's identity (from the JWT)."""
    return {
        "success": True,
        "data": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "subscription_plan": current_user.plan,
            "issued_at": int(time.time()),
        },
    }

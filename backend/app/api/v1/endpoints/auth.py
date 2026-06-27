"""Auth endpoints — login / signup / refresh / me.

Phase 1 used dev tokens. Phase 2 now proxies to Supabase Auth when
``SUPABASE_URL`` and ``SUPABASE_ANON_KEY`` are configured, with the
dev token fallback still available for local development and tests.
"""

from __future__ import annotations

import os
import time
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.middleware.auth import CurrentUser, get_current_user
from app.api.v1.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.config import settings
from app.utils.logger import get_logger

router = APIRouter()
log = get_logger(__name__)


def _supabase_env_present() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY)


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


async def _supabase_auth_request(endpoint: str, payload: dict) -> dict:
    """Proxy an auth request to Supabase Auth REST API."""
    url = f"{settings.SUPABASE_URL}/auth/v1/{endpoint}"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, headers=headers, json=payload)
        if resp.status_code >= 400:
            error_body = resp.json()
            raise HTTPException(
                status_code=resp.status_code,
                detail=error_body.get("error_description")
                or error_body.get("msg")
                or error_body.get("error", "Supabase auth request failed"),
            )
        return resp.json()


def _build_token_response(supabase_data: dict) -> TokenResponse:
    """Convert a Supabase auth response into our TokenResponse format."""
    return TokenResponse(
        access_token=supabase_data.get("access_token", ""),
        refresh_token=supabase_data.get("refresh_token"),
        expires_in=supabase_data.get("expires_in", 3600),
        user_id=supabase_data.get("user", {}).get("id", ""),
        email=supabase_data.get("user", {}).get("email", ""),
        subscription_plan=(
            supabase_data.get("user", {})
            .get("user_metadata", {})
            .get("subscription_plan", "free")
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    """Email/password login → Supabase access token."""
    if _supabase_env_present():
        try:
            supabase_data = await _supabase_auth_request("token?grant_type=password", {
                "email": payload.email,
                "password": payload.password,
            })
            log.info("auth.login_success", email=payload.email)
            # Get user metadata to check subscription plan
            user_id = supabase_data.get("user", {}).get("id", "")
            user_data = await _supabase_auth_request(f"user", {
                "apikey": settings.SUPABASE_ANON_KEY,
            })
            return TokenResponse(
                access_token=supabase_data.get("access_token", ""),
                refresh_token=supabase_data.get("refresh_token"),
                expires_in=supabase_data.get("expires_in", 3600),
                user_id=user_id,
                email=supabase_data.get("user", {}).get("email", payload.email),
                subscription_plan="free",
            )
        except HTTPException:
            raise
        except Exception as exc:
            log.error("auth.login_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication service unavailable",
            )

    # Dev fallback
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, payload.email))
    return _dev_token(user_id=user_id, email=payload.email)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest) -> TokenResponse:
    """Create a new user via Supabase Auth."""
    if _supabase_env_present():
        try:
            supabase_data = await _supabase_auth_request("signup", {
                "email": payload.email,
                "password": payload.password,
                "data": {
                    "full_name": payload.full_name or "",
                    "subscription_plan": "free",
                },
            })
            log.info("auth.signup_success", email=payload.email)
            return _build_token_response(supabase_data)
        except HTTPException:
            raise
        except Exception as exc:
            log.error("auth.signup_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Registration service unavailable",
            )

    # Dev fallback
    user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, payload.email))
    return _dev_token(user_id=user_id, email=payload.email)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str) -> TokenResponse:
    """Exchange a Supabase refresh_token for a new access_token."""
    if _supabase_env_present():
        try:
            supabase_data = await _supabase_auth_request("token?grant_type=refresh_token", {
                "refresh_token": refresh_token,
            })
            log.info("auth.refresh_success")
            return _build_token_response(supabase_data)
        except HTTPException:
            raise
        except Exception as exc:
            log.error("auth.refresh_error", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Authentication service unavailable",
            )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh tokens require Supabase configuration",
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
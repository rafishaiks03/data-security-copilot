"""
Authentication API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.core.config import get_settings
from backend.app.core.security import (
    create_access_token,
    verify_password,
)
from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)
from backend.app.services.users import get_user_by_username

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

settings = get_settings()


# ============================================================
# Login
# ============================================================


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
):
    """
    Authenticate a PostgreSQL-backed application user.
    """

    user = get_user_by_username(
        request.username,
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user["is_active"]:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not verify_password(
        request.password,
        user["password_hash"],
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    token = create_access_token(
        subject=str(user["user_id"]),
        additional_claims={
            "username": user["username"],
            "role": user["role"],
        },
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=(settings.jwt_access_token_expire_minutes * 60),
    )

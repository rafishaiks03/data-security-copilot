"""
FastAPI authentication and RBAC dependencies.
"""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.security import decode_access_token

security = HTTPBearer(
    auto_error=True,
)


# ============================================================
# Current authenticated user
# ============================================================


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate the JWT bearer token and return its claims.
    """

    token = credentials.credentials

    try:
        payload = decode_access_token(token)

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from exc

    return payload


# ============================================================
# Role-based access control
# ============================================================


def require_roles(
    *allowed_roles: str,
) -> Callable:

    def role_dependency(
        current_user: dict = Depends(get_current_user),
    ) -> dict:

        user_role = current_user.get("role")

        if user_role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Insufficient permissions. "
                    f"Required role: {', '.join(allowed_roles)}."
                ),
            )

        return current_user

    return role_dependency

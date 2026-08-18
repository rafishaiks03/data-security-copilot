"""
FastAPI authentication and authorization dependencies.
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.security import decode_access_token

# ============================================================
# HTTP Bearer authentication
# ============================================================

bearer_scheme = HTTPBearer(
    auto_error=True,
)


# ============================================================
# Get authenticated user
# ============================================================


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Validate the JWT access token and return its claims.
    """

    try:
        payload = decode_access_token(
            credentials.credentials,
        )

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
# Role-based authorization
# ============================================================


def require_roles(*allowed_roles: str) -> Callable:
    """
    Create a dependency that requires the authenticated user
    to have one of the specified roles.

    Example:

        Depends(require_roles("ADMIN"))

    or:

        Depends(require_roles("ADMIN", "INVESTIGATOR"))
    """

    normalized_roles = {role.upper() for role in allowed_roles}

    def role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:

        role = current_user.get("role")

        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is missing from access token.",
            )

        if role.upper() not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return role_checker

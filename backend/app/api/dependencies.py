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
    Validate the JWT bearer token and return a normalized
    authenticated-user object.
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

    # JWT subject contains the authenticated user's UUID.
    user_id = payload.get("sub")

    username = payload.get("username")
    role = payload.get("role")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a user ID.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a username.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a role.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    current_user = {
        "user_id": user_id,
        "username": username,
        "role": role,
    }

    print("CURRENT USER:", current_user)

    return current_user


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

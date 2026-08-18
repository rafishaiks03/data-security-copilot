"""
User management API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import require_roles
from backend.app.schemas.users import (
    UserCreateRequest,
    UserResponse,
)
from backend.app.services.users import create_user

router = APIRouter(
    prefix="/api/v1/users",
    tags=["User Management"],
)


# ============================================================
# Create user
# ============================================================


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application_user(
    request: UserCreateRequest,
    current_user: dict = Depends(require_roles("ADMIN")),
):
    """
    Create an application user.

    ADMIN only.
    """

    allowed_roles = {
        "ADMIN",
        "INVESTIGATOR",
        "VIEWER",
    }

    role = request.role.upper()

    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role.",
        )

    try:

        return create_user(
            username=request.username,
            password=request.password,
            role=role,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create user.",
        ) from exc

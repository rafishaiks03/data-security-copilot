"""
User management API endpoints.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from backend.app.api.dependencies import require_roles
from backend.app.schemas.users import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from backend.app.services.users import (
    create_user as create_user_service,
    get_user_by_id,
    list_users,
    update_user,
)

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
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
        )
    ),
):
    """
    Create a new application user.

    SECURITY_ADMIN only.
    """

    try:

        user = create_user_service(
            username=request.username,
            password=request.password,
            role=request.role,
        )

        return UserResponse(**user)

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user.",
        ) from exc


# ============================================================
# List users
# ============================================================


@router.get(
    "",
    response_model=UserListResponse,
)
def get_users(
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
        )
    ),
):
    """
    Return all application users.

    SECURITY_ADMIN only.
    """

    try:

        users = list_users()

        return UserListResponse(
            count=len(users),
            users=[UserResponse(**user) for user in users],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users.",
        ) from exc


# ============================================================
# Get user
# ============================================================


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_application_user(
    user_id: UUID,
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
        )
    ),
):
    """
    Return a single application user.

    SECURITY_ADMIN only.
    """

    user = get_user_by_id(
        str(user_id),
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse(**user)


# ============================================================
# Update user
# ============================================================


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
def update_application_user(
    user_id: UUID,
    request: UserUpdateRequest,
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
        )
    ),
):
    """
    Update a user's role or active status.

    SECURITY_ADMIN only.
    """

    if request.role is None and request.is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("At least one of 'role' or " "'is_active' must be provided."),
        )

    try:

        user = update_user(
            user_id=str(user_id),
            role=request.role,
            is_active=request.is_active,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user.",
        ) from exc

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return UserResponse(**user)

"""
User management API endpoints.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from backend.app.api.dependencies import require_roles
from backend.app.schemas.users import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from backend.app.services.audit import create_audit_log
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
    request: Request,
    user_request: UserCreateRequest,
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
            username=user_request.username,
            password=user_request.password,
            role=user_request.role,
        )
        print("CURRENT USER:", current_user)
        print("CURRENT USER SUB:", current_user.get("sub"))
        print("CREATED USER ID:", user["user_id"])
        create_audit_log(
            user_id=current_user.get("user_id"),
            username=current_user.get("username"),
            action="CREATE_USER",
            resource_type="USER",
            resource_id=str(user["user_id"]),
            details={
                "created_username": user["username"],
                "created_role": user["role"],
            },
            ip_address=request.client.host if request.client else None,
        )

        return UserResponse(**user)

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print("CREATE USER ERROR:", repr(exc))

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
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
    user_request: UserUpdateRequest,
    request: Request,
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

    if user_request.role is None and user_request.is_active is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("At least one of 'role' or " "'is_active' must be provided."),
        )

    # Get the existing user first so that the audit event
    # can record what changed.
    existing_user = get_user_by_id(
        str(user_id),
    )

    if existing_user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    try:

        user = update_user(
            user_id=str(user_id),
            role=user_request.role,
            is_active=user_request.is_active,
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

    create_audit_log(
        user_id=current_user.get("user_id"),
        username=current_user.get("username"),
        action="UPDATE_USER",
        resource_type="USER",
        resource_id=str(user_id),
        details={
            "target_username": user["username"],
            "old_role": existing_user["role"],
            "new_role": user["role"],
            "old_is_active": existing_user["is_active"],
            "new_is_active": user["is_active"],
        },
        ip_address=request.client.host if request.client else None,
    )

    return UserResponse(**user)

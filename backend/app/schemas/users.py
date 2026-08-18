"""
User management API schemas.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_ROLES = {
    "SECURITY_ADMIN",
    "SECURITY_ANALYST",
    "AUDITOR",
}


class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
    )

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role: str = "AUDITOR"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.upper()

        if value not in ALLOWED_ROLES:
            raise ValueError(
                "Invalid role. Allowed roles: "
                "SECURITY_ADMIN, SECURITY_ANALYST, AUDITOR."
            )

        return value


class UserUpdateRequest(BaseModel):
    role: str | None = None
    is_active: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.upper()

        if value not in ALLOWED_ROLES:
            raise ValueError(
                "Invalid role. Allowed roles: "
                "SECURITY_ADMIN, SECURITY_ANALYST, AUDITOR."
            )

        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    count: int
    users: list[UserResponse]

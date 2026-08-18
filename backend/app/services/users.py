"""
User management and authentication service.
"""

from __future__ import annotations

from typing import Any

from backend.app.core.security import hash_password
from backend.app.db.database import get_database_connection

ALLOWED_ROLES = {
    "SECURITY_ADMIN",
    "SECURITY_ANALYST",
    "AUDITOR",
}


def create_user(
    username: str,
    password: str,
    role: str = "AUDITOR",
) -> dict[str, Any]:
    """
    Create a PostgreSQL-backed application user.
    """

    role = role.upper()

    if role not in ALLOWED_ROLES:
        raise ValueError(
            "Invalid role. Allowed roles: " "SECURITY_ADMIN, SECURITY_ANALYST, AUDITOR."
        )

    password_hash = hash_password(password)

    query = """
        INSERT INTO users (
            username,
            password_hash,
            role
        )
        VALUES (%s, %s, %s)
        RETURNING
            user_id,
            username,
            role,
            is_active,
            created_at,
            updated_at
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    username,
                    password_hash,
                    role,
                ),
            )

            row = cursor.fetchone()

            columns = [description.name for description in cursor.description]

        connection.commit()

    return dict(zip(columns, row))


def get_user_by_username(
    username: str,
) -> dict[str, Any] | None:
    """
    Retrieve a user including the password hash.
    """

    query = """
        SELECT
            user_id,
            username,
            password_hash,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE username = %s
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (username,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [description.name for description in cursor.description]

    return dict(zip(columns, row))


def list_users() -> list[dict[str, Any]]:
    """
    Return all application users.

    Password hashes are intentionally excluded.
    """

    query = """
        SELECT
            user_id,
            username,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        ORDER BY created_at DESC
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [description.name for description in cursor.description]

    return [dict(zip(columns, row)) for row in rows]


def get_user_by_id(
    user_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve a user by ID.

    Password hashes are intentionally excluded.
    """

    query = """
        SELECT
            user_id,
            username,
            role,
            is_active,
            created_at,
            updated_at
        FROM users
        WHERE user_id = %s
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (user_id,),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [description.name for description in cursor.description]

    return dict(zip(columns, row))


def update_user(
    user_id: str,
    role: str | None = None,
    is_active: bool | None = None,
) -> dict[str, Any] | None:
    """
    Update a user's role and/or active status.
    """

    if role is None and is_active is None:
        raise ValueError("At least one user attribute must be provided.")

    if role is not None:

        role = role.upper()

        if role not in ALLOWED_ROLES:
            raise ValueError(
                "Invalid role. Allowed roles: "
                "SECURITY_ADMIN, SECURITY_ANALYST, AUDITOR."
            )

    query = """
        UPDATE users
        SET
            role = COALESCE(%s, role),
            is_active = COALESCE(%s, is_active),
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s
        RETURNING
            user_id,
            username,
            role,
            is_active,
            created_at,
            updated_at
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    role,
                    is_active,
                    user_id,
                ),
            )

            row = cursor.fetchone()

            if row is None:
                return None

            columns = [description.name for description in cursor.description]

        connection.commit()

    return dict(zip(columns, row))

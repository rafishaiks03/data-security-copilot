"""
User management and authentication service.
"""

from __future__ import annotations

from typing import Any

from backend.app.core.security import hash_password
from backend.app.db.database import get_database_connection


def create_user(
    username: str,
    password: str,
    role: str = "VIEWER",
) -> dict[str, Any]:
    """
    Create a PostgreSQL-backed application user.
    """

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

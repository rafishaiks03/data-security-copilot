"""
Audit logging service.
"""

from __future__ import annotations

from typing import Any

from psycopg.types.json import Jsonb

from backend.app.db.database import get_database_connection


def create_audit_log(
    *,
    user_id: str | None,
    username: str | None,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> None:
    """
    Create an immutable security audit event.
    """

    query = """
        INSERT INTO audit_logs (
            user_id,
            username,
            action,
            resource_type,
            resource_id,
            details,
            ip_address
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    with get_database_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    user_id,
                    username,
                    action,
                    resource_type,
                    resource_id,
                    Jsonb(details) if details is not None else None,
                    ip_address,
                ),
            )

        connection.commit()

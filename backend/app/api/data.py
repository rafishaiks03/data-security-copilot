"""
Data Explorer API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import require_roles
from app.db.database import get_database_connection

router = APIRouter(
    prefix="/api/v1/data",
    tags=["Data Explorer"],
)


@router.get("/tables")
def list_tables(
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
            "SECURITY_ANALYST",
            "AUDITOR",
        )
    ),
):
    """
    Return user-accessible tables from the public schema.
    """

    query = """
        SELECT
            table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """

    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        tables = [row[0] for row in rows]

        return {
            "count": len(tables),
            "tables": tables,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve database tables.",
        ) from exc

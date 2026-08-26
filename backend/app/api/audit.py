"""
Security audit log API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.api.dependencies import require_roles
from app.db.database import get_database_connection
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
)

router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["Security Audit"],
)


# ============================================================
# List audit logs
# ============================================================


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def list_audit_logs(
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
        )
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    action: str | None = Query(
        default=None,
    ),
    username: str | None = Query(
        default=None,
    ),
    resource_type: str | None = Query(
        default=None,
    ),
    resource_id: UUID | None = Query(
        default=None,
    ),
):
    """
    Return security audit events.

    SECURITY_ADMIN only.

    Supports filtering by:
    - action
    - username
    - resource type
    - resource ID

    Supports pagination using:
    - limit
    - offset
    """

    conditions: list[str] = []
    parameters: list[object] = []

    # --------------------------------------------------------
    # Optional filters
    # --------------------------------------------------------

    if action is not None:
        conditions.append("action = %s")
        parameters.append(action.upper())

    if username is not None:
        conditions.append("username = %s")
        parameters.append(username)

    if resource_type is not None:
        conditions.append("resource_type = %s")
        parameters.append(resource_type.upper())

    if resource_id is not None:
        conditions.append("resource_id = %s")
        parameters.append(str(resource_id))

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # --------------------------------------------------------
    # Count query
    # --------------------------------------------------------

    count_query = f"""
        SELECT COUNT(*)
        FROM audit_logs
        {where_clause}
    """

    # --------------------------------------------------------
    # Data query
    # --------------------------------------------------------

    query = f"""
        SELECT
            audit_id,
            user_id,
            username,
            action,
            resource_type,
            resource_id,
            details,
            ip_address,
            created_at
        FROM audit_logs
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
        OFFSET %s
    """

    parameters_with_pagination = [
        *parameters,
        limit,
        offset,
    ]

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                # --------------------------------------------
                # Total matching records
                # --------------------------------------------

                cursor.execute(
                    count_query,
                    parameters,
                )

                total_count = cursor.fetchone()[0]

                # --------------------------------------------
                # Requested page
                # --------------------------------------------

                cursor.execute(
                    query,
                    parameters_with_pagination,
                )

                rows = cursor.fetchall()

                columns = [description.name for description in cursor.description]

        audit_logs = [
            dict(
                zip(
                    columns,
                    row,
                )
            )
            for row in rows
        ]

        return AuditLogListResponse(
            count=total_count,
            audit_logs=[AuditLogResponse(**log) for log in audit_logs],
        )

    except Exception as exc:

        print(
            "AUDIT LOG RETRIEVAL ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs.",
        ) from exc

"""
Security audit log API endpoints.
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from backend.app.api.dependencies import require_roles
from backend.app.db.database import get_database_connection
from backend.app.schemas.audit import (
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
):
    """
    Return recent security audit events.

    SECURITY_ADMIN only.
    """

    query = """
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
        ORDER BY created_at DESC
        LIMIT %s
    """

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (limit,),
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
            count=len(audit_logs),
            audit_logs=[AuditLogResponse(**log) for log in audit_logs],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs.",
        ) from exc

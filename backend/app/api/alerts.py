"""
Fraud alert API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.api.dependencies import require_roles

from backend.app.db.database import get_database_connection
from backend.app.schemas.alerts import (
    AlertListResponse,
    AlertResponse,
    AlertUpdateRequest,
)

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Fraud Alerts"],
)


# ============================================================
# List alerts
# ============================================================


@router.get(
    "",
    response_model=AlertListResponse,
)
def list_alerts(
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
            "SECURITY_ANALYST",
            "AUDITOR",
        )
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
):
    """
    Return the most recent fraud alerts.
    """

    query = """
        SELECT
            alert_id,
            transaction_id,
            customer_id,
            alert_type,
            risk_score,
            risk_level,
            model_name,
            model_version,
            reason,
            features,
            status,
            reviewed_by,
            reviewed_at,
            created_at,
            updated_at
        FROM fraud_alerts
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

        alerts = [
            dict(
                zip(
                    columns,
                    row,
                )
            )
            for row in rows
        ]

        return AlertListResponse(
            count=len(alerts),
            alerts=alerts,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alerts.",
        ) from exc


# ============================================================
# Get single alert
# ============================================================


@router.get(
    "/{alert_id}",
    response_model=AlertResponse,
)
def get_alert(
    alert_id: str,
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
            "SECURITY_ANALYST",
            "AUDITOR",
        )
    ),
):
    """
    Return a single fraud alert by alert_id.
    """

    query = """
        SELECT
            alert_id,
            transaction_id,
            customer_id,
            alert_type,
            risk_score,
            risk_level,
            model_name,
            model_version,
            reason,
            features,
            status,
            reviewed_by,
            reviewed_at,
            created_at,
            updated_at
        FROM fraud_alerts
        WHERE alert_id = %s
    """

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (alert_id,),
                )

                row = cursor.fetchone()

                if row is None:

                    raise HTTPException(
                        status_code=404,
                        detail="Fraud alert not found.",
                    )

                columns = [description.name for description in cursor.description]

        alert = dict(
            zip(
                columns,
                row,
            )
        )

        return AlertResponse(**alert)

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alert.",
        ) from exc


# ============================================================
# Update alert
# ============================================================


@router.patch(
    "/{alert_id}",
    response_model=AlertResponse,
)
def update_alert(
    alert_id: str,
    request: AlertUpdateRequest,
    current_user: dict = Depends(
        require_roles(
            "SECURITY_ADMIN",
            "SECURITY_ANALYST",
        )
    ),
):
    """
    Update the status of a fraud alert.

    ADMIN and INVESTIGATOR users can update alerts.
    VIEWER users cannot.
    """

    allowed_statuses = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
        "FALSE_POSITIVE",
    }

    new_status = request.status.upper()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid alert status. "
                "Allowed values: OPEN, INVESTIGATING, "
                "RESOLVED, FALSE_POSITIVE."
            ),
        )

    query = """
        UPDATE fraud_alerts
        SET
            status = %s,
            reviewed_by = %s,
            reviewed_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE alert_id = %s
        RETURNING
            alert_id,
            transaction_id,
            customer_id,
            alert_type,
            risk_score,
            risk_level,
            model_name,
            model_version,
            reason,
            features,
            status,
            reviewed_by,
            reviewed_at,
            created_at,
            updated_at
    """

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        new_status,
                        current_user.get("username"),
                        alert_id,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Fraud alert not found.",
                    )

                columns = [description.name for description in cursor.description]

            connection.commit()

        alert = dict(
            zip(
                columns,
                row,
            )
        )

        return AlertResponse(**alert)

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to update fraud alert.",
        ) from exc

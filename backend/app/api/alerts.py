"""
Fraud alert API endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import require_roles
from app.db.database import get_database_connection
from app.schemas.alerts import (
    AlertListResponse,
    AlertResponse,
    AlertUpdateRequest,
)
from app.services.audit import create_audit_log

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Fraud Alerts"],
)


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
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                columns = [description.name for description in cursor.description]

        alerts = [dict(zip(columns, row)) for row in rows]

        return AlertListResponse(
            count=len(alerts),
            alerts=alerts,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alerts.",
        ) from exc


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
                cursor.execute(query, (alert_id,))
                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Fraud alert not found.",
                    )

                columns = [description.name for description in cursor.description]

        alert = dict(zip(columns, row))

        return AlertResponse(**alert)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alert.",
        ) from exc


@router.get(
    "/{alert_id}/transaction",
)
def get_alert_transaction(
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
    Return the transaction associated with a fraud alert.

    This endpoint is used by the Alert Detail page to display
    transaction evidence related to the selected fraud alert.
    """

    query = """
        SELECT
            t.transaction_id,
            t.sender_account_id,
            t.receiver_account_id,
            t.transaction_type_code,
            t.amount,
            t.currency_code,
            t.transaction_timestamp,
            t.device_id,
            t.ip_address,
            t.country_code,
            t.status,
            t.description,
            t.created_at,
            t.known_fraud_label
        FROM fraud_alerts a
        LEFT JOIN transactions t
            ON t.transaction_id = a.transaction_id
        WHERE a.alert_id = %s
    """

    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (alert_id,))
                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Fraud alert not found.",
                    )

                columns = [description.name for description in cursor.description]

        transaction = dict(zip(columns, row))

        if transaction["transaction_id"] is None:
            raise HTTPException(
                status_code=404,
                detail="Transaction evidence not found for this alert.",
            )

        return transaction

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve transaction evidence.",
        ) from exc


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

        alert = dict(zip(columns, row))

        create_audit_log(
            user_id=current_user.get("user_id"),
            username=current_user.get("username"),
            action="UPDATE_ALERT",
            resource_type="FRAUD_ALERT",
            resource_id=alert_id,
            details={
                "new_status": new_status,
            },
        )

        return AlertResponse(**alert)

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to update fraud alert.",
        ) from exc

"""
Fraud alert API endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.db.database import get_database_connection

router = APIRouter(
    prefix="/api/v1/alerts",
    tags=["Fraud Alerts"],
)


# ============================================================
# Request models
# ============================================================


class AlertStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="New alert status.",
    )

    reviewed_by: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Analyst reviewing the alert.",
    )


# ============================================================
# List alerts
# ============================================================


@router.get("")
def list_alerts(
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

        return {
            "count": len(alerts),
            "alerts": alerts,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alerts.",
        ) from exc


# ============================================================
# Get single alert
# ============================================================


@router.get("/{alert_id}")
def get_alert(
    alert_id: str,
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

        return dict(
            zip(
                columns,
                row,
            )
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve fraud alert.",
        ) from exc


# ============================================================
# Update alert status
# ============================================================


@router.patch("/{alert_id}")
def update_alert(
    alert_id: str,
    update: AlertStatusUpdate,
):
    """
    Update the status and reviewer information for a fraud alert.
    """

    allowed_statuses = {
        "OPEN",
        "INVESTIGATING",
        "RESOLVED",
    }

    if update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Allowed values: " "OPEN, INVESTIGATING, RESOLVED."
            ),
        )

    query = """
        UPDATE fraud_alerts
        SET
            status = %s,
            reviewed_by = %s,
            reviewed_at = %s,
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

    reviewed_at = datetime.now(timezone.utc)

    try:

        with get_database_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        update.status,
                        update.reviewed_by,
                        reviewed_at,
                        alert_id,
                    ),
                )

                row = cursor.fetchone()

                if row is None:

                    connection.rollback()

                    raise HTTPException(
                        status_code=404,
                        detail="Fraud alert not found.",
                    )

                columns = [description.name for description in cursor.description]

            connection.commit()

        return dict(
            zip(
                columns,
                row,
            )
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to update fraud alert.",
        ) from exc


# ============================================================
# Alert investigation details
# ============================================================


@router.get("/{alert_id}/investigation")
def get_alert_investigation(
    alert_id: str,
):
    """
    Return an investigation view for a fraud alert.

    Includes:
    - alert information
    - transaction information
    - sender account information
    - sender customer information
    """

    query = """
        SELECT
            fa.alert_id,
            fa.alert_type,
            fa.risk_score,
            fa.risk_level,
            fa.model_name,
            fa.model_version,
            fa.reason,
            fa.features,
            fa.status AS alert_status,
            fa.reviewed_by,
            fa.reviewed_at,
            fa.created_at AS alert_created_at,

            t.transaction_id,
            t.transaction_type_code,
            t.amount,
            t.currency_code,
            t.transaction_timestamp,
            t.country_code,
            t.status AS transaction_status,
            t.description,

            a.account_id,
            a.account_number,
            a.account_type,
            a.status AS account_status,

            c.customer_id,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            c.country_code AS customer_country_code

        FROM fraud_alerts fa

        JOIN transactions t
            ON t.transaction_id = fa.transaction_id

        LEFT JOIN accounts a
            ON a.account_id = t.sender_account_id

        LEFT JOIN customers c
            ON c.customer_id = a.customer_id

        WHERE fa.alert_id = %s
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

                columns = [
                    description.name
                    for description in cursor.description
                ]

        data = dict(zip(columns, row))

        return {
            "alert": {
                "alert_id": data["alert_id"],
                "alert_type": data["alert_type"],
                "risk_score": data["risk_score"],
                "risk_level": data["risk_level"],
                "model_name": data["model_name"],
                "model_version": data["model_version"],
                "reason": data["reason"],
                "features": data["features"],
                "status": data["alert_status"],
                "reviewed_by": data["reviewed_by"],
                "reviewed_at": data["reviewed_at"],
                "created_at": data["alert_created_at"],
            },
            "transaction": {
                "transaction_id": data["transaction_id"],
                "transaction_type_code": data["transaction_type_code"],
                "amount": data["amount"],
                "currency_code": data["currency_code"],
                "transaction_timestamp": data["transaction_timestamp"],
                "country_code": data["country_code"],
                "status": data["transaction_status"],
                "description": data["description"],
            },
            "account": {
                "account_id": data["account_id"],
                "account_number": data["account_number"],
                "account_type": data["account_type"],
                "status": data["account_status"],
            },
            "customer": {
                "customer_id": data["customer_id"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"],
                "phone": data["phone"],
                "country_code": data["customer_country_code"],
            },
        }

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve investigation details.",
        ) from exc
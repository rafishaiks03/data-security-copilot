"""
Pydantic schemas for fraud alert API responses.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# Alert features
# ============================================================


class AlertFeatures(BaseModel):
    """
    ML features associated with a fraud alert.
    """

    model_config = ConfigDict(extra="allow")

    amount: Decimal | None = None
    is_night: int | None = None
    missing_device: int | None = None
    amount_last_24h: Decimal | None = None
    transaction_hour: int | None = None
    is_large_transaction: int | None = None
    transactions_last_24h: int | None = None
    transaction_day_of_week: int | None = None
    distinct_devices_last_30d: int | None = None
    is_very_large_transaction: int | None = None


# ============================================================
# Alert response
# ============================================================


class AlertResponse(BaseModel):
    """
    Public API representation of a fraud alert.
    """

    model_config = ConfigDict(from_attributes=True)

    alert_id: UUID
    transaction_id: UUID | None = None
    customer_id: UUID | None = None

    alert_type: str
    risk_score: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
    )
    risk_level: str

    model_name: str | None = None
    model_version: str | None = None

    reason: str | None = None
    features: dict[str, Any] | None = None

    status: str
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime


# ============================================================
# Alert list response
# ============================================================


class AlertListResponse(BaseModel):
    """
    Paginated-style response for fraud alerts.
    """

    count: int = Field(ge=0)
    alerts: list[AlertResponse]


class AlertUpdateRequest(BaseModel):
    status: str

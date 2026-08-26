"""
Audit log API schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from ipaddress import IPv4Address, IPv6Address


class AuditLogResponse(BaseModel):
    """
    Represents a security audit event.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    audit_id: UUID
    user_id: UUID | None
    username: str | None
    action: str
    resource_type: str | None
    resource_id: UUID | None
    details: dict[str, Any] | None
    ip_address: IPv4Address | IPv6Address | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """
    Paginated-style response containing audit events.
    """

    count: int
    audit_logs: list[AuditLogResponse]

"""Audit event definitions with proper typing.

This module defines strongly typed audit events using TypedDict and dataclasses
for type safety and validation.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, TypedDict


class AuditOperation(Enum):
    """Standardized audit operations for billing service."""

    CUSTOMER_CREATE = "customer.create"
    CUSTOMER_UPDATE = "customer.update"
    USAGE_TRACK = "usage.track"
    INVOICE_CREATE = "invoice.create"
    INVOICE_UPDATE = "invoice.update"
    PAYMENT_PROCESS = "payment.process"
    WEBHOOK_PROCESS = "webhook.process"
    PRICING_UPDATE = "pricing.update"
    BILLING_PERIOD_CREATE = "billing_period.create"
    BILLING_PERIOD_CLOSE = "billing_period.close"


class AuditEventDict(TypedDict):
    """Typed dictionary for audit events storage.

    This provides type safety for the dictionary representation
    used in DynamoDB storage.
    """

    # Required fields
    event_id: str
    timestamp: str
    operation: str
    entity_type: str
    entity_id: str

    # Optional fields
    correlation_id: Optional[str]
    user_id: Optional[str]
    before_state: Optional[dict[str, Any]]
    after_state: Optional[dict[str, Any]]
    metadata: dict[str, Any]
    error: Optional[str]
    duration_ms: Optional[int]


@dataclass
class AuditEvent:
    """Structured audit event with automatic field generation.

    This class provides a type-safe way to create audit events with
    automatic generation of timestamps and unique IDs.
    """

    # Core required fields
    operation: str
    entity_type: str
    entity_id: str

    # Auto-generated fields
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Optional context fields
    correlation_id: Optional[str] = None
    user_id: Optional[str] = "system"
    before_state: Optional[dict[str, Any]] = None
    after_state: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: Optional[int] = None

    def to_dict(self) -> AuditEventDict:
        """Convert to typed dictionary for storage.

        Returns:
            AuditEventDict suitable for DynamoDB storage
        """
        return AuditEventDict(
            event_id=self.event_id,
            timestamp=self.timestamp.isoformat(),
            operation=self.operation,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            correlation_id=self.correlation_id,
            user_id=self.user_id,
            before_state=self.before_state,
            after_state=self.after_state,
            metadata=self.metadata,
            error=self.error,
            duration_ms=self.duration_ms,
        )

    @classmethod
    def from_dict(cls, data: AuditEventDict) -> "AuditEvent":
        """Create event from dictionary.

        Args:
            data: Dictionary representation of audit event

        Returns:
            AuditEvent instance
        """
        timestamp_str = data["timestamp"]
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        return cls(
            event_id=data["event_id"],
            timestamp=timestamp,
            operation=data["operation"],
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            correlation_id=data.get("correlation_id"),
            user_id=data.get("user_id"),
            before_state=data.get("before_state"),
            after_state=data.get("after_state"),
            metadata=data.get("metadata", {}),
            error=data.get("error"),
            duration_ms=data.get("duration_ms"),
        )

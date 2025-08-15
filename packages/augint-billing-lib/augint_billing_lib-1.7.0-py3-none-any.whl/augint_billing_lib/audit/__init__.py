"""Audit logging for the Augint Billing Library.

This module provides production-grade audit logging with:
- Structured audit events with proper typing
- DynamoDB storage with retry logic and circuit breaker
- Sensitive data redaction
- Thread-safe context management
- Automatic method auditing via decorators
- Compression for large events
- Graceful degradation on failures

Example:
    Basic audit logging:

    >>> from augint_billing_lib.audit import AuditLogger, DynamoDBAuditStorage
    >>>
    >>> storage = DynamoDBAuditStorage(table_name="billing-data-dev")
    >>> logger = AuditLogger(storage=storage)
    >>>
    >>> logger.log_operation(
    ...     operation="customer.create",
    ...     entity_type="customer",
    ...     entity_id="CUST123"
    ... )

    With context tracking:

    >>> from augint_billing_lib.audit import AuditContext
    >>>
    >>> with AuditContext(correlation_id="req-123", user_id="user456"):
    ...     logger.log_operation("usage.track", "usage", "CUST123")

    Automatic method auditing:

    >>> from augint_billing_lib.audit import audited, AuditOperation
    >>>
    >>> class BillingService:
    ...     def __init__(self, audit_logger: AuditLogger):
    ...         self.audit_logger = audit_logger
    ...
    ...     @audited(AuditOperation.USAGE_TRACK, "usage", "customer_id")
    ...     def track_usage(self, customer_id: str, count: int):
    ...         # Automatically audited with timing
    ...         pass
"""

# Core components
from .config import AuditConfig, get_audit_config, reset_audit_config
from .context import AuditContext
from .decorator import audited
from .events import AuditEvent, AuditEventDict, AuditOperation
from .logger import AuditLogger, TimingAuditLogger, create_timing_logger
from .redaction import RedactionPattern, SensitiveDataRedactor
from .storage import AuditStorage, DynamoDBAuditStorage

__all__ = [
    "AuditConfig",
    "AuditContext",
    "AuditEvent",
    "AuditEventDict",
    "AuditLogger",
    "AuditOperation",
    "AuditStorage",
    "DynamoDBAuditStorage",
    "RedactionPattern",
    "SensitiveDataRedactor",
    "TimingAuditLogger",
    "audited",
    "create_timing_logger",
    "get_audit_config",
    "reset_audit_config",
]

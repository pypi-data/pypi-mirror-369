"""Core audit logger implementation.

This module provides the main AuditLogger class with clean separation
of concerns and production-ready error handling.
"""

import logging
import time
from typing import Any, Optional

from ..exceptions import BillingError
from .context import AuditContext
from .events import AuditEvent
from .redaction import SensitiveDataRedactor
from .storage import AuditStorage

logger = logging.getLogger(__name__)


class AuditLogger:
    """Core audit logger with clean separation of concerns.

    This class orchestrates audit logging by delegating to specialized
    components. It has ONE responsibility: coordinate audit event creation
    and storage.
    """

    def __init__(
        self,
        storage: Optional[AuditStorage] = None,
        redactor: Optional[SensitiveDataRedactor] = None,
        enable_redaction: bool = True,
    ):
        """Initialize audit logger.

        Args:
            storage: Storage backend for audit events
            redactor: Data redactor (uses default if None)
            enable_redaction: Whether to redact sensitive data
        """
        self.storage = storage
        self.redactor = redactor or SensitiveDataRedactor()
        self.enable_redaction = enable_redaction

    def log_operation(
        self,
        operation: str,
        entity_type: str,
        entity_id: str,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        **metadata: Any,
    ) -> None:
        """Log an operation with comprehensive error handling.

        Args:
            operation: Operation being performed
            entity_type: Type of entity being operated on
            entity_id: Identifier of the entity
            before_state: State before operation
            after_state: State after operation
            error: Error message if operation failed
            duration_ms: Operation duration in milliseconds
            **metadata: Additional metadata
        """
        try:
            # Create audit event
            event = self._create_event(
                operation=operation,
                entity_type=entity_type,
                entity_id=entity_id,
                before_state=before_state,
                after_state=after_state,
                error=error,
                duration_ms=duration_ms,
                metadata=metadata,
            )

            # Store event if storage is available
            if self.storage:
                self.storage.store(event)

            logger.debug(f"Audit logged: {operation} for {entity_type}:{entity_id}")

        except Exception as e:
            # Never fail the main operation due to audit logging
            logger.exception(f"Audit logging failed for {operation}")

            # Only raise if storage is critical
            if self.storage and self.storage.is_critical:
                raise BillingError(f"Critical audit failure: {e}") from e

    def _create_event(
        self,
        operation: str,
        entity_type: str,
        entity_id: str,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AuditEvent:
        """Create audit event with context and redaction.

        Args:
            operation: Operation name
            entity_type: Entity type
            entity_id: Entity ID
            before_state: State before operation
            after_state: State after operation
            error: Error message
            duration_ms: Duration in milliseconds
            metadata: Additional metadata

        Returns:
            Created audit event
        """
        # Get context information
        context = AuditContext.get_current()
        correlation_id = context.correlation_id if context else None
        user_id = context.user_id if context else None

        # Add context metadata if available
        event_metadata = metadata.copy() if metadata else {}
        if context and context.metadata:
            event_metadata.update(context.metadata)

        # Redact sensitive data if enabled
        if self.enable_redaction:
            if before_state:
                before_state = self.redactor.redact(before_state)
            if after_state:
                after_state = self.redactor.redact(after_state)
            if event_metadata:
                event_metadata = self.redactor.redact(event_metadata)

        # Create event (only pass user_id if it's not None to allow default to apply)
        event_args: dict[str, Any] = {
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "correlation_id": correlation_id,
            "before_state": before_state,
            "after_state": after_state,
            "error": error,
            "duration_ms": duration_ms,
            "metadata": event_metadata,
        }

        if user_id is not None:
            event_args["user_id"] = user_id

        return AuditEvent(**event_args)


def create_timing_logger(audit_logger: AuditLogger) -> "TimingAuditLogger":
    """Create a timing audit logger wrapper.

    Args:
        audit_logger: Base audit logger to wrap

    Returns:
        TimingAuditLogger that automatically measures durations
    """
    return TimingAuditLogger(audit_logger)


class TimingAuditLogger:
    """Audit logger wrapper that automatically tracks operation timing.

    This provides a convenient way to measure and log operation durations.
    """

    def __init__(self, audit_logger: AuditLogger):
        """Initialize timing logger.

        Args:
            audit_logger: Base audit logger to wrap
        """
        self.audit_logger = audit_logger

    def log_timed_operation(
        self,
        operation: str,
        entity_type: str,
        entity_id: str,
        start_time: float,
        before_state: Optional[dict[str, Any]] = None,
        after_state: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        **metadata: Any,
    ) -> None:
        """Log operation with automatic duration calculation.

        Args:
            operation: Operation name
            entity_type: Entity type
            entity_id: Entity ID
            start_time: Start time from time.perf_counter()
            before_state: State before operation
            after_state: State after operation
            error: Error message
            **metadata: Additional metadata
        """
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        self.audit_logger.log_operation(
            operation=operation,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state,
            after_state=after_state,
            error=error,
            duration_ms=duration_ms,
            **metadata,
        )

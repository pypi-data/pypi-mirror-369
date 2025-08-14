"""Thread-safe audit context management.

This module provides thread-safe context management for tracking
correlation IDs and audit metadata across operations.
"""

import contextvars
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

# Thread-safe context variable
_audit_context: contextvars.ContextVar[Optional["AuditContext"]] = contextvars.ContextVar(
    "audit_context", default=None
)


@dataclass
class AuditContext:
    """Thread-safe audit context for correlation tracking.

    This context manager provides a way to track correlation IDs
    and other metadata across audit operations in a thread-safe manner.
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __enter__(self) -> "AuditContext":
        """Enter context and set as current."""
        self._token = _audit_context.set(self)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and restore previous."""
        _audit_context.reset(self._token)

    @classmethod
    def get_current(cls) -> Optional["AuditContext"]:
        """Get the current audit context if any.

        Returns:
            Current AuditContext or None if not in context
        """
        return _audit_context.get()

    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get current correlation ID if in context.

        Returns:
            Correlation ID or None if not in context
        """
        current = cls.get_current()
        return current.correlation_id if current else None

    @classmethod
    def get_user_id(cls) -> Optional[str]:
        """Get current user ID if in context.

        Returns:
            User ID or None if not in context
        """
        current = cls.get_current()
        return current.user_id if current else None

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the context.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

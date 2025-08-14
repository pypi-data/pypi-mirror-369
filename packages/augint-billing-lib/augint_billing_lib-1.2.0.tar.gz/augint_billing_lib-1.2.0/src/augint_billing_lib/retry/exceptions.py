"""Retry-specific exceptions for the billing service.

This module defines exception classes for retry operations, circuit breaker
patterns, and related error handling scenarios.
"""

from typing import Any, Optional


class RetryError(Exception):
    """Base exception for all retry-related errors.

    Attributes:
        message: Human-readable error message
        details: Additional error context
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize retry error.

        Args:
            message: Error message
            details: Optional additional context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class RetryableError(RetryError):
    """Raised for errors that can be retried.

    This exception indicates that an operation failed due to a transient error
    and can be safely retried according to the retry policy.
    """

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize retryable error.

        Args:
            message: Error message
            original_error: Original exception that caused the retry
            **kwargs: Additional context to include in details
        """
        details = kwargs.copy()
        if original_error:
            details["original_error"] = str(original_error)
            details["original_error_type"] = type(original_error).__name__

        super().__init__(message=message, details=details)
        self.original_error = original_error


class MaxRetriesExceededError(RetryError):
    """Raised when maximum retry attempts have been exceeded.

    This exception indicates that all retry attempts have been exhausted
    and the operation could not be completed successfully.
    """

    def __init__(
        self,
        operation: str,
        max_retries: int,
        last_error: Optional[Exception] = None,
        total_delay: Optional[float] = None,
    ) -> None:
        """Initialize max retries exceeded error.

        Args:
            operation: Name of the operation that failed
            max_retries: Maximum number of retries that were attempted
            last_error: Last error that occurred before giving up
            total_delay: Total time spent in retry delays
        """
        message = f"Maximum retries ({max_retries}) exceeded for operation: {operation}"

        details = {
            "operation": operation,
            "max_retries": max_retries,
        }

        if last_error:
            details["last_error"] = str(last_error)
            details["last_error_type"] = type(last_error).__name__

        if total_delay is not None:
            details["total_delay_seconds"] = total_delay

        super().__init__(message=message, details=details)
        self.operation = operation
        self.max_retries = max_retries
        self.last_error = last_error
        self.total_delay = total_delay


class CircuitBreakerError(RetryError):
    """Raised when circuit breaker is in open state.

    This exception indicates that the circuit breaker is currently open
    and preventing calls to the external service to avoid cascading failures.
    """

    def __init__(
        self,
        service_name: str,
        state: str,
        failure_count: int,
        next_attempt_time: Optional[float] = None,
    ) -> None:
        """Initialize circuit breaker error.

        Args:
            service_name: Name of the service with open circuit breaker
            state: Current circuit breaker state
            failure_count: Number of recent failures
            next_attempt_time: When the next attempt will be allowed (timestamp)
        """
        message = f"Circuit breaker OPEN for service '{service_name}' - calls blocked"

        details = {
            "service_name": service_name,
            "circuit_state": state,
            "failure_count": failure_count,
        }

        if next_attempt_time is not None:
            details["next_attempt_time"] = next_attempt_time

        super().__init__(message=message, details=details)
        self.service_name = service_name
        self.state = state
        self.failure_count = failure_count
        self.next_attempt_time = next_attempt_time

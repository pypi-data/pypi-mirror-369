"""Circuit breaker implementation for preventing cascading failures.

This module implements the circuit breaker pattern to protect external services
from being overwhelmed during failure scenarios and to fail fast when services
are known to be unavailable.
"""

import threading
import time
from enum import Enum
from typing import Any, Optional, TypeVar

from .exceptions import CircuitBreakerError

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states.

    CLOSED: Normal operation, all calls allowed
    OPEN: All calls fail fast, no external calls made
    HALF_OPEN: Limited calls allowed to test recovery
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation for external service protection.

    The circuit breaker monitors failures and transitions between states:
    - CLOSED: Normal operation, calls are allowed
    - OPEN: Calls fail immediately without attempting external service
    - HALF_OPEN: Single test call allowed to check if service has recovered

    This prevents cascading failures and provides fast failure feedback
    when external services are known to be unavailable.

    Example:
        Basic usage with context manager:

        >>> circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        >>>
        >>> try:
        ...     with circuit_breaker:
        ...         result = external_service_call()
        ... except CircuitBreakerError:
        ...     # Circuit is open, service unavailable
        ...     handle_service_unavailable()

        Usage with explicit call tracking:

        >>> circuit_breaker = CircuitBreaker()
        >>>
        >>> if circuit_breaker.can_call():
        ...     try:
        ...         result = external_service_call()
        ...         circuit_breaker.record_success()
        ...     except Exception as e:
        ...         circuit_breaker.record_failure(e)
        ...         raise
        ... else:
        ...     raise CircuitBreakerError(...)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type[Exception] = Exception,
        name: Optional[str] = None,
    ) -> None:
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before transitioning to half-open
            expected_exception: Exception type that triggers failure counting
            name: Optional name for logging and metrics
        """
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")
        if timeout <= 0:
            raise ValueError("timeout must be > 0")

        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name or "unnamed"

        # State management
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_attempts = 0

        # Thread safety
        self._lock = threading.RLock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit breaker state."""
        with self._lock:
            return self._state

    @property
    def failure_count(self) -> int:
        """Get current failure count."""
        with self._lock:
            return self._failure_count

    def can_call(self) -> bool:
        """Check if a call can be made based on circuit breaker state.

        Returns:
            True if call is allowed, False if circuit is open
        """
        with self._lock:
            current_time = time.time()

            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                # Check if timeout has elapsed to transition to half-open
                if current_time - self._last_failure_time >= self.timeout:
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_attempts = 0
                    return True
                return False
            # HALF_OPEN state - allow limited calls
            # Allow limited calls in half-open state
            return self._half_open_attempts == 0

    def record_success(self) -> None:
        """Record a successful call.

        This resets the failure count and transitions to CLOSED state
        if currently in HALF_OPEN state.
        """
        with self._lock:
            self._failure_count = 0

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED

    def record_failure(self, exception: Exception) -> None:
        """Record a failed call.

        Args:
            exception: Exception that caused the failure
        """
        with self._lock:
            # Only count expected exceptions as failures
            if isinstance(exception, self.expected_exception):
                self._failure_count += 1
                self._last_failure_time = time.time()

                if self._state == CircuitState.HALF_OPEN:
                    # Failed test call, go back to open
                    self._state = CircuitState.OPEN
                elif self._failure_count >= self.failure_threshold:
                    # Threshold exceeded, open the circuit
                    self._state = CircuitState.OPEN

    def reset(self) -> None:
        """Reset circuit breaker to CLOSED state.

        This is primarily useful for testing or manual recovery scenarios.
        """
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._last_failure_time = 0.0
            self._half_open_attempts = 0

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics.

        Returns:
            Dictionary with current state and statistics
        """
        with self._lock:
            current_time = time.time()

            stats = {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "failure_threshold": self.failure_threshold,
                "timeout": self.timeout,
                "last_failure_time": self._last_failure_time,
            }

            if self._state == CircuitState.OPEN:
                time_until_half_open = max(
                    0, self.timeout - (current_time - self._last_failure_time)
                )
                stats["time_until_half_open"] = time_until_half_open

            return stats

    def __enter__(self) -> "CircuitBreaker":
        """Enter context manager.

        Raises:
            CircuitBreakerError: If circuit is open and calls are not allowed
        """
        if not self.can_call():
            raise CircuitBreakerError(
                service_name=self.name,
                state=self._state.value,
                failure_count=self._failure_count,
                next_attempt_time=self._last_failure_time + self.timeout,
            )

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_attempts += 1

        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any) -> None:
        """Exit context manager, recording success or failure."""
        if exc_type is None:
            # Success
            self.record_success()
        elif exc_val is not None:
            # Failure
            self.record_failure(exc_val)


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers by service name.

    This class provides a centralized way to manage circuit breakers for
    different services, ensuring each service has its own circuit breaker
    instance with appropriate configuration.
    """

    def __init__(self) -> None:
        """Initialize circuit breaker registry."""
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._lock = threading.RLock()

    def get_circuit_breaker(
        self,
        service_name: str,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type[Exception] = Exception,
    ) -> CircuitBreaker:
        """Get or create a circuit breaker for a service.

        Args:
            service_name: Name of the service
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before transitioning to half-open
            expected_exception: Exception type that triggers failure counting

        Returns:
            CircuitBreaker instance for the service
        """
        with self._lock:
            if service_name not in self._circuit_breakers:
                self._circuit_breakers[service_name] = CircuitBreaker(
                    failure_threshold=failure_threshold,
                    timeout=timeout,
                    expected_exception=expected_exception,
                    name=service_name,
                )

            return self._circuit_breakers[service_name]

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all registered circuit breakers.

        Returns:
            Dictionary mapping service names to their circuit breaker stats
        """
        with self._lock:
            return {
                service_name: cb.get_stats() for service_name, cb in self._circuit_breakers.items()
            }

    def reset_all(self) -> None:
        """Reset all circuit breakers to CLOSED state."""
        with self._lock:
            for cb in self._circuit_breakers.values():
                cb.reset()

    def reset_service(self, service_name: str) -> None:
        """Reset a specific service's circuit breaker.

        Args:
            service_name: Name of the service to reset

        Raises:
            KeyError: If service is not registered
        """
        with self._lock:
            if service_name not in self._circuit_breakers:
                raise KeyError(f"No circuit breaker registered for service: {service_name}")

            self._circuit_breakers[service_name].reset()


# Global circuit breaker registry
_global_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
    timeout: int = 60,
    expected_exception: type[Exception] = Exception,
) -> CircuitBreaker:
    """Get a circuit breaker for a service from the global registry.

    Args:
        service_name: Name of the service
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds to wait before transitioning to half-open
        expected_exception: Exception type that triggers failure counting

    Returns:
        CircuitBreaker instance for the service
    """
    return _global_registry.get_circuit_breaker(
        service_name=service_name,
        failure_threshold=failure_threshold,
        timeout=timeout,
        expected_exception=expected_exception,
    )


def get_all_circuit_breaker_stats() -> dict[str, dict[str, Any]]:
    """Get statistics for all circuit breakers in the global registry.

    Returns:
        Dictionary mapping service names to their circuit breaker stats
    """
    return _global_registry.get_all_stats()


def reset_all_circuit_breakers() -> None:
    """Reset all circuit breakers in the global registry."""
    _global_registry.reset_all()


def reset_circuit_breaker(service_name: str) -> None:
    """Reset a specific circuit breaker in the global registry.

    Args:
        service_name: Name of the service to reset
    """
    _global_registry.reset_service(service_name)

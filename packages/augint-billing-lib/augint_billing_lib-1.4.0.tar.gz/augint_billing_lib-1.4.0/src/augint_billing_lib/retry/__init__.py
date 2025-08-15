"""Retry logic with exponential backoff and circuit breaker patterns.

This module provides production-grade retry mechanisms for external service calls
in the Augint Billing Library. It implements exponential backoff with jitter,
circuit breaker patterns, and service-specific retry policies.

Key Components:
    - retry_with_backoff: Core retry decorator with exponential backoff
    - RetryConfig: Configuration class for retry policies
    - ServiceRetryConfigs: Pre-configured retry policies for different services
    - CircuitBreaker: Circuit breaker implementation for cascading failure prevention

Example:
    Basic retry decorator usage:

    >>> from augint_billing_lib.retry import retry_with_backoff
    >>>
    >>> @retry_with_backoff(max_retries=3, base_delay=1.0)
    >>> def external_api_call():
    ...     # API call implementation
    ...     pass

    Service-specific retry policies:

    >>> from augint_billing_lib.retry import ServiceRetryConfigs
    >>>
    >>> @retry_with_backoff(**ServiceRetryConfigs.STRIPE.to_dict())
    >>> def stripe_api_call():
    ...     # Stripe API call with pre-configured retry policy
    ...     pass

    Circuit breaker integration:

    >>> from augint_billing_lib.retry import CircuitBreaker
    >>>
    >>> circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    >>> with circuit_breaker:
    ...     # External service call
    ...     pass
"""

# Import all public components
from .circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    get_circuit_breaker,
    reset_all_circuit_breakers,
)
from .config import RetryConfig, ServiceRetryConfigs, is_retryable_error
from .core import calculate_delay, retry_with_backoff
from .exceptions import (
    CircuitBreakerError,
    MaxRetriesExceededError,
    RetryableError,
    RetryError,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",
    "MaxRetriesExceededError",
    "RetryConfig",
    "RetryError",
    "RetryableError",
    "ServiceRetryConfigs",
    "calculate_delay",
    "get_circuit_breaker",
    "is_retryable_error",
    "reset_all_circuit_breakers",
    "retry_with_backoff",
]

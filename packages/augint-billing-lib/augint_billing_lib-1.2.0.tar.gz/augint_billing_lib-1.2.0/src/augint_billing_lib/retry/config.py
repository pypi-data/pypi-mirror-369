"""Configuration classes for retry policies and service-specific settings.

This module provides configuration management for retry logic, including
service-specific retry policies, circuit breaker settings, and error
classification rules.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional

import stripe
import stripe.error
from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-untyped]


@dataclass
class RetryConfig:
    """Configuration for retry policies with exponential backoff.

    This class defines all parameters for retry behavior including backoff
    calculations, error handling, and circuit breaker integration.

    Attributes:
        max_retries: Maximum number of retry attempts (0 = no retries)
        base_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation (2^n)
        jitter: Whether to add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exception types that can be retried
        circuit_breaker_enabled: Whether to enable circuit breaker for this service
        timeout: Maximum total time to spend on retries (seconds)
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = ()
    circuit_breaker_enabled: bool = False
    timeout: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.base_delay <= 0:
            raise ValueError("base_delay must be > 0")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if self.exponential_base <= 1:
            raise ValueError("exponential_base must be > 1")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout must be > 0")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary for decorator parameters.

        Returns:
            Dictionary representation suitable for passing to retry decorator
        """
        return {
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_base": self.exponential_base,
            "jitter": self.jitter,
            "retryable_exceptions": self.retryable_exceptions,
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
            "timeout": self.timeout,
        }

    @classmethod
    def from_env(
        cls,
        prefix: str,
        **overrides: Any,
    ) -> "RetryConfig":
        """Create configuration from environment variables.

        Args:
            prefix: Environment variable prefix (e.g., "RETRY_STRIPE_")
            **overrides: Override specific values

        Returns:
            RetryConfig instance with values from environment
        """

        def get_env_int(key: str, default: int) -> int:
            value = os.environ.get(f"{prefix}{key}")
            return int(value) if value is not None else default

        def get_env_float(key: str, default: float) -> float:
            value = os.environ.get(f"{prefix}{key}")
            return float(value) if value is not None else default

        def get_env_bool(key: str, default: bool) -> bool:
            value = os.environ.get(f"{prefix}{key}")
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")

        config_dict: dict[str, Any] = {
            "max_retries": get_env_int("MAX_ATTEMPTS", 3),
            "base_delay": get_env_float("BASE_DELAY", 1.0),
            "max_delay": get_env_float("MAX_DELAY", 60.0),
            "exponential_base": get_env_float("EXPONENTIAL_BASE", 2.0),
            "jitter": get_env_bool("JITTER", True),
            "circuit_breaker_enabled": get_env_bool("CIRCUIT_BREAKER_ENABLED", False),
        }

        timeout_str = os.environ.get(f"{prefix}TIMEOUT")
        if timeout_str:
            config_dict["timeout"] = float(timeout_str)

        # Apply overrides
        config_dict.update(overrides)

        return cls(**config_dict)


class ServiceRetryConfigs:
    """Pre-configured retry policies for different external services.

    This class provides service-specific retry configurations optimized
    for each external service's characteristics and requirements.
    """

    # Stripe API retry configuration
    # Stripe has good rate limiting and transient error handling
    # Use moderate retries with exponential backoff
    STRIPE = RetryConfig(
        max_retries=int(os.environ.get("RETRY_STRIPE_MAX_ATTEMPTS", "3")),
        base_delay=float(os.environ.get("RETRY_STRIPE_BASE_DELAY", "1.0")),
        max_delay=float(os.environ.get("RETRY_STRIPE_MAX_DELAY", "60.0")),
        exponential_base=2.0,
        jitter=True,
        retryable_exceptions=(
            stripe.error.RateLimitError,  # type: ignore[attr-defined]
            stripe.error.APIConnectionError,  # type: ignore[attr-defined]
            stripe.error.APIError,  # type: ignore[attr-defined]
            ConnectionError,
            TimeoutError,
        ),
        circuit_breaker_enabled=True,
        timeout=300.0,  # 5 minutes total timeout for billing operations
    )

    # DynamoDB retry configuration
    # DynamoDB has built-in retries but we add our own for throttling
    # Use more aggressive retries due to pay-per-request pricing model
    DYNAMODB = RetryConfig(
        max_retries=int(os.environ.get("RETRY_DYNAMODB_MAX_ATTEMPTS", "5")),
        base_delay=float(os.environ.get("RETRY_DYNAMODB_BASE_DELAY", "0.1")),
        max_delay=float(os.environ.get("RETRY_DYNAMODB_MAX_DELAY", "30.0")),
        exponential_base=2.0,
        jitter=True,
        retryable_exceptions=(
            ClientError,  # Covers throttling and service errors
            BotoCoreError,
            ConnectionError,
            TimeoutError,
        ),
        circuit_breaker_enabled=True,
        timeout=120.0,  # 2 minutes total timeout for database operations
    )

    # EventBridge retry configuration
    # EventBridge events are less critical, use fewer retries
    # Focus on delivery but don't block billing operations
    EVENTBRIDGE = RetryConfig(
        max_retries=int(os.environ.get("RETRY_EVENTBRIDGE_MAX_ATTEMPTS", "2")),
        base_delay=float(os.environ.get("RETRY_EVENTBRIDGE_BASE_DELAY", "0.5")),
        max_delay=float(os.environ.get("RETRY_EVENTBRIDGE_MAX_DELAY", "10.0")),
        exponential_base=2.0,
        jitter=True,
        retryable_exceptions=(
            ClientError,  # AWS service errors
            BotoCoreError,
            ConnectionError,
            TimeoutError,
        ),
        circuit_breaker_enabled=False,  # Don't block on event failures
        timeout=30.0,  # 30 seconds timeout for event publishing
    )

    # Secrets Manager retry configuration
    # Secrets Manager calls are infrequent but critical
    # Use moderate retries with shorter timeouts
    SECRETS_MANAGER = RetryConfig(
        max_retries=int(os.environ.get("RETRY_SECRETS_MAX_ATTEMPTS", "3")),
        base_delay=float(os.environ.get("RETRY_SECRETS_BASE_DELAY", "0.5")),
        max_delay=float(os.environ.get("RETRY_SECRETS_MAX_DELAY", "15.0")),
        exponential_base=2.0,
        jitter=True,
        retryable_exceptions=(
            ClientError,
            BotoCoreError,
            ConnectionError,
            TimeoutError,
        ),
        circuit_breaker_enabled=False,  # Don't circuit break config access
        timeout=60.0,  # 1 minute timeout for secrets access
    )

    @classmethod
    def get_config(cls, service_name: str) -> RetryConfig:
        """Get retry configuration for a specific service.

        Args:
            service_name: Name of the service (stripe, dynamodb, eventbridge, etc.)

        Returns:
            RetryConfig for the specified service

        Raises:
            ValueError: If service_name is not recognized
        """
        service_configs = {
            "stripe": cls.STRIPE,
            "dynamodb": cls.DYNAMODB,
            "eventbridge": cls.EVENTBRIDGE,
            "secrets_manager": cls.SECRETS_MANAGER,
        }

        config = service_configs.get(service_name.lower())
        if config is None:
            available = ", ".join(service_configs.keys())
            raise ValueError(f"Unknown service '{service_name}'. Available: {available}")

        return config


def is_retryable_error(  # noqa: PLR0911
    error: Exception, retryable_exceptions: tuple[type[Exception], ...]
) -> bool:
    """Check if an error is retryable based on exception type and error details.

    This function implements sophisticated error classification logic that goes
    beyond simple exception type checking to examine error codes and messages.

    Args:
        error: Exception to check
        retryable_exceptions: Tuple of exception types that are generally retryable

    Returns:
        True if the error should be retried, False otherwise
    """
    # Check for general network/connection errors first
    if isinstance(error, (ConnectionError, TimeoutError, OSError)):
        return True

    # Check if error type is in retryable exceptions
    if not isinstance(error, retryable_exceptions):
        return False

    # Additional checks for specific error types

    # Stripe error classification
    if isinstance(error, stripe.error.StripeError):  # type: ignore[attr-defined]
        # Don't retry authentication or permission errors
        non_retryable_stripe = (
            stripe.error.AuthenticationError,  # type: ignore[attr-defined]
            stripe.error.PermissionError,  # type: ignore[attr-defined]
            stripe.error.InvalidRequestError,  # type: ignore[attr-defined]
            stripe.error.SignatureVerificationError,  # type: ignore[attr-defined]
        )
        if isinstance(error, non_retryable_stripe):
            return False

        # Don't retry client errors (4xx) except rate limits
        if hasattr(error, "http_status") and error.http_status:
            is_client_error = 400 <= error.http_status < 500
            is_rate_limit = error.http_status == 429
            return not is_client_error or is_rate_limit

    # AWS/Boto3 error classification
    elif isinstance(error, ClientError):
        error_code = error.response.get("Error", {}).get("Code", "")

        # Check against non-retryable and retryable code sets
        non_retryable_codes = {
            "ValidationException",
            "InvalidParameterValue",
            "AccessDenied",
            "UnauthorizedOperation",
            "ResourceNotFoundException",
            "ConditionalCheckFailedException",  # DynamoDB conditional failures
        }

        retryable_codes = {
            "ProvisionedThroughputExceededException",  # DynamoDB throttling
            "ThrottlingException",
            "ServiceUnavailableException",
            "InternalServerError",
            "LimitExceededException",
        }

        # Check error codes
        if error_code in non_retryable_codes:
            return False
        if error_code in retryable_codes:
            return True

        # Check HTTP status for 5xx errors
        if hasattr(error, "response"):
            status_code = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            if status_code and 500 <= status_code < 600:
                return True

    # Default to retryable for other known exception types in retryable_exceptions
    return True

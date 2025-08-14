"""Core retry logic with exponential backoff and jitter.

This module implements the main retry decorator with sophisticated backoff
algorithms, error classification, and circuit breaker integration for
production-grade reliability.
"""

import asyncio
import functools
import secrets
import time
from collections.abc import Awaitable
from typing import Any, Callable, Optional, TypeVar, Union, cast

from .circuit_breaker import get_circuit_breaker
from .config import is_retryable_error
from .exceptions import CircuitBreakerError, MaxRetriesExceededError

F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T")


def calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> float:
    """Calculate delay for retry attempt with exponential backoff and jitter.

    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds for this attempt
    """
    # Calculate exponential delay: base_delay * (exponential_base ^ attempt)
    delay = base_delay * (exponential_base**attempt)

    # Apply maximum delay limit
    delay = min(delay, max_delay)

    # Add jitter to prevent thundering herd effect
    if jitter:
        # Add random jitter up to 25% of the calculated delay
        # Using secrets for cryptographically secure randomness
        jitter_amount = delay * 0.25 * (secrets.SystemRandom().random())
        delay += jitter_amount

    return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
    circuit_breaker_enabled: bool = False,
    circuit_breaker_service: Optional[str] = None,
    circuit_breaker_failure_threshold: int = 5,
    circuit_breaker_timeout: int = 60,
    timeout: Optional[float] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable[[F], F]:
    """Decorator for retrying operations with exponential backoff and jitter.

    This decorator provides comprehensive retry functionality including:
    - Exponential backoff with configurable parameters
    - Random jitter to prevent thundering herd effects
    - Selective retrying based on exception types
    - Circuit breaker integration for cascading failure prevention
    - Total timeout enforcement
    - Retry attempt callbacks for logging/metrics

    Args:
        max_retries: Maximum number of retry attempts (0 = no retries)
        base_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay in seconds between retries
        exponential_base: Base for exponential backoff calculation (2^n)
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exception types that can be retried
        circuit_breaker_enabled: Whether to enable circuit breaker protection
        circuit_breaker_service: Service name for circuit breaker (defaults to function name)
        circuit_breaker_failure_threshold: Failures before opening circuit
        circuit_breaker_timeout: Seconds before transitioning to half-open
        timeout: Maximum total time to spend on retries (None = no limit)
        on_retry: Optional callback for retry attempts: (attempt, exception, delay) -> None

    Returns:
        Decorated function with retry logic

    Example:
        Basic retry with default settings:

        >>> @retry_with_backoff(max_retries=3)
        >>> def api_call():
        ...     # API call implementation
        ...     pass

        Custom retry policy with circuit breaker:

        >>> @retry_with_backoff(
        ...     max_retries=5,
        ...     base_delay=0.5,
        ...     retryable_exceptions=(ConnectionError, TimeoutError),
        ...     circuit_breaker_enabled=True,
        ...     circuit_breaker_service="external_api"
        ... )
        >>> def external_service_call():
        ...     # External service call
        ...     pass
    """

    def decorator(func: F) -> F:
        # Determine circuit breaker service name
        service_name = circuit_breaker_service or func.__name__

        # Get circuit breaker if enabled
        circuit_breaker = None
        if circuit_breaker_enabled:
            circuit_breaker = get_circuit_breaker(
                service_name=service_name,
                failure_threshold=circuit_breaker_failure_threshold,
                timeout=circuit_breaker_timeout,
                expected_exception=retryable_exceptions[0] if retryable_exceptions else Exception,
            )

        if asyncio.iscoroutinefunction(func):
            # Async version
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await _execute_with_retry(
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    max_retries=max_retries,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                    retryable_exceptions=retryable_exceptions,
                    circuit_breaker=circuit_breaker,
                    timeout=timeout,
                    on_retry=on_retry,
                    is_async=True,
                )

            return cast(F, async_wrapper)

        # Sync version
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            return _execute_with_retry(
                func=func,
                args=args,
                kwargs=kwargs,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                retryable_exceptions=retryable_exceptions,
                circuit_breaker=circuit_breaker,
                timeout=timeout,
                on_retry=on_retry,
                is_async=False,
            )

        return cast(F, sync_wrapper)

    return decorator


def _execute_with_retry(
    func: Callable[..., Union[T, Awaitable[T]]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    max_retries: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool,
    retryable_exceptions: tuple[type[Exception], ...],
    circuit_breaker: Any,
    timeout: Optional[float],
    on_retry: Optional[Callable[[int, Exception, float], None]],
    is_async: bool,
) -> Union[T, Awaitable[T]]:
    """Execute function with retry logic.

    This is the core retry implementation that handles both sync and async functions.
    """
    if is_async:
        return _execute_async_with_retry(
            func=func,  # type: ignore[arg-type]
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
            retryable_exceptions=retryable_exceptions,
            circuit_breaker=circuit_breaker,
            timeout=timeout,
            on_retry=on_retry,
        )
    return _execute_sync_with_retry(
        func=func,
        args=args,
        kwargs=kwargs,
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        circuit_breaker=circuit_breaker,
        timeout=timeout,
        on_retry=on_retry,
    )


def _execute_sync_with_retry(  # noqa: PLR0912, PLR0915
    func: Callable[..., T],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    max_retries: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool,
    retryable_exceptions: tuple[type[Exception], ...],
    circuit_breaker: Any,
    timeout: Optional[float],
    on_retry: Optional[Callable[[int, Exception, float], None]],
) -> T:
    """Synchronous retry execution."""
    start_time = time.time()
    last_exception: Optional[Exception] = None
    total_delay = 0.0

    for attempt in range(max_retries + 1):  # +1 for initial attempt
        # Check circuit breaker before each attempt
        if circuit_breaker is not None:
            try:
                with circuit_breaker:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        raise
            except CircuitBreakerError:
                # Circuit is open, fail immediately
                raise
            except Exception as e:
                last_exception = e

                # Check if we should retry this error
                if not is_retryable_error(e, retryable_exceptions):
                    raise

                # Check if we've exhausted retries
                if attempt >= max_retries:
                    break

                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Calculate delay for next attempt
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                )

                # Check if delay would exceed timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + delay >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Call retry callback if provided
                if on_retry is not None:
                    on_retry(attempt + 1, e, delay)

                # Sleep before retry
                time.sleep(delay)
                total_delay += delay
        else:
            # No circuit breaker, direct execution with retry
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if we should retry this error
                if not is_retryable_error(e, retryable_exceptions):
                    raise

                # Check if we've exhausted retries
                if attempt >= max_retries:
                    break

                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Calculate delay for next attempt
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                )

                # Check if delay would exceed timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + delay >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Call retry callback if provided
                if on_retry is not None:
                    on_retry(attempt + 1, e, delay)

                # Sleep before retry
                time.sleep(delay)
                total_delay += delay

    # All retries exhausted
    raise MaxRetriesExceededError(
        operation=func.__name__,
        max_retries=max_retries,
        last_error=last_exception,
        total_delay=total_delay,
    )


async def _execute_async_with_retry(  # noqa: PLR0912, PLR0915
    func: Callable[..., Awaitable[T]],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    max_retries: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool,
    retryable_exceptions: tuple[type[Exception], ...],
    circuit_breaker: Any,
    timeout: Optional[float],
    on_retry: Optional[Callable[[int, Exception, float], None]],
) -> T:
    """Asynchronous retry execution."""
    start_time = time.time()
    last_exception: Optional[Exception] = None
    total_delay = 0.0

    for attempt in range(max_retries + 1):  # +1 for initial attempt
        # Check circuit breaker before each attempt
        if circuit_breaker is not None:
            try:
                with circuit_breaker:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        raise
            except CircuitBreakerError:
                # Circuit is open, fail immediately
                raise
            except Exception as e:
                last_exception = e

                # Check if we should retry this error
                if not is_retryable_error(e, retryable_exceptions):
                    raise

                # Check if we've exhausted retries
                if attempt >= max_retries:
                    break

                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Calculate delay for next attempt
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                )

                # Check if delay would exceed timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + delay >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Call retry callback if provided
                if on_retry is not None:
                    on_retry(attempt + 1, e, delay)

                # Async sleep before retry
                await asyncio.sleep(delay)
                total_delay += delay
        else:
            # No circuit breaker, direct execution with retry
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if we should retry this error
                if not is_retryable_error(e, retryable_exceptions):
                    raise

                # Check if we've exhausted retries
                if attempt >= max_retries:
                    break

                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Calculate delay for next attempt
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                )

                # Check if delay would exceed timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed + delay >= timeout:
                        raise MaxRetriesExceededError(
                            operation=func.__name__,
                            max_retries=max_retries,
                            last_error=e,
                            total_delay=total_delay,
                        )

                # Call retry callback if provided
                if on_retry is not None:
                    on_retry(attempt + 1, e, delay)

                # Async sleep before retry
                await asyncio.sleep(delay)
                total_delay += delay

    # All retries exhausted
    raise MaxRetriesExceededError(
        operation=func.__name__,
        max_retries=max_retries,
        last_error=last_exception,
        total_delay=total_delay,
    )

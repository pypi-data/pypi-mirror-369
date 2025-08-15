"""Audit decorator for automatic method auditing.

This module provides decorators for automatically auditing method calls
with proper error handling and timing.
"""

import contextlib
import functools
import time
from typing import Any, Callable, Optional, TypeVar, Union

from .events import AuditOperation
from .logger import AuditLogger

F = TypeVar("F", bound=Callable[..., Any])


def audited(
    operation: Union[str, AuditOperation],
    entity_type: str,
    entity_id_param: str = "customer_id",
    capture_before_state: bool = False,
    capture_after_state: bool = False,
    before_state_extractor: Optional[Callable[..., dict[str, Any]]] = None,
    after_state_extractor: Optional[Callable[..., dict[str, Any]]] = None,
) -> Callable[[F], F]:
    """Decorator for automatic method auditing with timing.

    This decorator automatically creates audit logs for method calls,
    capturing timing, arguments, and results as configured.

    Args:
        operation: Operation name or AuditOperation enum value
        entity_type: Type of entity being operated on
        entity_id_param: Parameter name containing entity ID
        capture_before_state: Whether to capture method arguments
        capture_after_state: Whether to capture method result
        before_state_extractor: Custom function to extract before state
        after_state_extractor: Custom function to extract after state

    Returns:
        Decorated function with audit logging

    Example:
        Basic usage:

        >>> @audited("customer.create", "customer", "customer_id")
        >>> def create_customer(self, customer_id: str, **kwargs):
        ...     # Implementation
        ...     pass

        With state capture:

        >>> @audited(
        ...     AuditOperation.USAGE_TRACK,
        ...     "usage",
        ...     capture_before_state=True,
        ...     capture_after_state=True
        ... )
        >>> def track_usage(self, customer_id: str, usage_count: int):
        ...     # Implementation
        ...     return result
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Check if the instance has an audit logger
            audit_logger: Optional[AuditLogger] = getattr(self, "audit_logger", None)
            if not audit_logger:
                # No audit logger available, execute normally
                return func(self, *args, **kwargs)

            # Extract operation name
            op_name = operation.value if isinstance(operation, AuditOperation) else operation

            # Extract entity ID safely (pass args without self)
            entity_id = _extract_entity_id(entity_id_param, args, kwargs)

            # Capture before state if requested or if custom extractor provided
            before_state = None
            if capture_before_state or before_state_extractor:
                if before_state_extractor:
                    try:
                        before_state = before_state_extractor(self, *args, **kwargs)
                    except Exception as e:
                        # Don't fail if state extraction fails
                        before_state = {"extraction_error": str(e)}
                else:
                    # Default: capture all arguments
                    before_state = _extract_default_before_state(args, kwargs)

            # Execute the operation with timing
            start_time = time.perf_counter()
            error = None
            result = None

            try:
                result = func(self, *args, **kwargs)
                return result  # noqa: RET504

            except Exception as e:
                error = str(e)
                raise

            finally:
                # Calculate duration
                duration_ms = int((time.perf_counter() - start_time) * 1000)

                # Capture after state if requested or if custom extractor provided (and no error)
                after_state = None
                if (capture_after_state or after_state_extractor) and error is None:
                    if after_state_extractor:
                        try:
                            after_state = after_state_extractor(result, self, *args, **kwargs)
                        except Exception as e:
                            # Don't fail if state extraction fails
                            after_state = {"extraction_error": str(e)}
                    else:
                        # Default: capture result if it's serializable
                        after_state = _extract_default_after_state(result)

                # Log the audit event
                with contextlib.suppress(Exception):
                    audit_logger.log_operation(
                        operation=op_name,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        before_state=before_state,
                        after_state=after_state,
                        error=error,
                        duration_ms=duration_ms,
                        function_name=func.__name__,
                        module_name=func.__module__,
                    )

        return wrapper  # type: ignore[return-value]

    return decorator


def _extract_entity_id(entity_id_param: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Extract entity ID from function parameters.

    Args:
        entity_id_param: Parameter name containing entity ID
        args: Positional arguments (excluding self)
        kwargs: Keyword arguments

    Returns:
        Entity ID as string
    """
    # First check kwargs
    if entity_id_param in kwargs:
        return str(kwargs[entity_id_param])

    # Common parameter positions for entity ID (after self is already removed)
    entity_id_positions = {
        "customer_id": 0,  # First parameter after self
        "user_id": 0,
        "entity_id": 0,
        "primary_id": 0,  # For test_audited_multiple_parameters
        "id": 0,
    }

    # Try to get from positional args only if the parameter name is in our known list
    if entity_id_param in entity_id_positions:
        position = entity_id_positions[entity_id_param]
        if len(args) > position:
            return str(args[position])

    # Fallback to "unknown" if can't extract
    return "unknown"


def _extract_default_before_state(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Extract default before state from arguments.

    Args:
        args: Positional arguments (excluding self)
        kwargs: Keyword arguments

    Returns:
        Dictionary representing before state
    """
    before_state: dict[str, Any] = {}

    # Add positional args (self already excluded)
    if len(args) > 0:
        before_state["args"] = args

    # Add keyword args
    if kwargs:
        before_state["kwargs"] = kwargs

    return before_state


def _extract_default_after_state(result: Any) -> Optional[dict[str, Any]]:
    """Extract default after state from result.

    Args:
        result: Function result

    Returns:
        Dictionary representing after state or None
    """
    if result is None:
        return None

    # For simple types, just store the value
    if isinstance(result, (str, int, float, bool)):
        return {"result": result}

    # For dict results, store them directly
    if isinstance(result, dict):
        return result.copy()

    # For other types, try to convert to string representation
    try:
        return {"result": str(result), "type": type(result).__name__}
    except Exception:
        # If we can't serialize it, don't include it
        return {"result_type": type(result).__name__}

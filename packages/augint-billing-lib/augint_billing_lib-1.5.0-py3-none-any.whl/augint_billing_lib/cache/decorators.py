"""Cache decorators for clean integration."""

import functools
import inspect
import logging
import re
from typing import Any, Callable, TypeVar, cast

from .protocol import CacheProtocol

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _generate_cache_key(
    pattern: str,
    instance: Any,
    func: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> str:
    """Generate cache key from pattern.

    Supports:
    - {arg_name} - Replace with argument value
    - {class_name} - Replace with class name
    - {method_name} - Replace with method name
    - {0}, {1}, etc - Replace with positional args
    """
    key = pattern

    # Replace class and method names
    key = key.replace("{class_name}", instance.__class__.__name__)
    key = key.replace("{method_name}", func.__name__)

    # Get function signature for mapping args to names
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())[1:]  # Skip 'self'

    # Build arg mapping
    arg_map = {}
    for i, (param_name, arg_value) in enumerate(zip(param_names, args)):
        arg_map[param_name] = arg_value
        arg_map[str(i)] = arg_value
    arg_map.update(kwargs)

    # Replace placeholders
    for placeholder, value in arg_map.items():
        key = key.replace(f"{{{placeholder}}}", str(value))

    return key


def cached(
    ttl: int = 300,
    key_pattern: str = "{class_name}:{method_name}:{0}",
) -> Callable[[F], F]:
    """Decorator for caching method results.

    Args:
        ttl: Time to live in seconds
        key_pattern: Pattern for cache key generation

    Example:
        @cached(ttl=600, key_pattern="customer:{customer_id}")
        def get_customer(self, customer_id: str) -> Customer:
            return self._fetch_from_db(customer_id)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Get cache from instance
            cache = getattr(self, "_cache", None)
            if not cache or not (
                isinstance(cache, CacheProtocol)
                or (hasattr(cache, "get") and hasattr(cache, "set"))
            ):
                # No cache available, execute normally
                return func(self, *args, **kwargs)

            # Generate cache key
            cache_key = _generate_cache_key(key_pattern, self, func, args, kwargs)

            # Try to get from cache
            try:
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
            except (KeyError, AttributeError, TypeError) as e:
                logger.warning(f"Cache get failed for key {cache_key}: {e}")
                # Continue without cache
            except Exception as e:
                logger.error(f"Unexpected cache get error: {e}", exc_info=True)
                # Continue without cache

            # Execute function
            result = func(self, *args, **kwargs)

            # Cache result if not None
            if result is not None:
                try:
                    cache.set(cache_key, result, ttl)
                except (KeyError, AttributeError, TypeError) as e:
                    logger.warning(f"Cache set failed for key {cache_key}: {e}")
                    # Continue without cache
                except Exception as e:
                    logger.error(f"Unexpected cache set error: {e}", exc_info=True)
                    # Continue without cache

            return result

        # Store metadata for testing/debugging
        wrapper._cache_ttl = ttl  # type: ignore[attr-defined]
        wrapper._cache_key_pattern = key_pattern  # type: ignore[attr-defined]

        return cast(F, wrapper)

    return decorator


def cache_invalidate(
    patterns: list[str],
) -> Callable[[F], F]:
    """Decorator to invalidate cache entries after method execution.

    Args:
        patterns: List of key patterns to invalidate
                 Supports wildcards: "customer:*" invalidates all customer keys

    Example:
        @cache_invalidate(["customer:{customer_id}", "customer:list:*"])
        def update_customer(self, customer_id: str, data: dict):
            return self._update_in_db(customer_id, data)
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Execute function first
            result = func(self, *args, **kwargs)

            # Get cache from instance
            cache = getattr(self, "_cache", None)
            if not cache or not (
                isinstance(cache, CacheProtocol)
                or (hasattr(cache, "delete") and hasattr(cache, "clear"))
            ):
                return result

            # Invalidate cache entries
            for pattern in patterns:
                try:
                    # Generate actual key from pattern
                    key = _generate_cache_key(pattern, self, func, args, kwargs)

                    # Handle wildcards with proper pattern matching
                    if "*" in key:
                        # Convert wildcard to regex
                        regex_pattern = "^" + re.escape(key).replace("\\*", ".*") + "$"
                        compiled = re.compile(regex_pattern)

                        # Find and delete matching keys
                        if hasattr(cache, "get_all_keys"):
                            for cache_key in cache.get_all_keys():
                                if compiled.match(cache_key):
                                    cache.delete(cache_key)
                        else:
                            # Fallback to clear if cache doesn't support key listing
                            cache.clear()
                    else:
                        cache.delete(key)
                except (KeyError, AttributeError, TypeError) as e:
                    logger.warning(f"Cache invalidation failed for pattern {pattern}: {e}")
                    # Don't fail on cache errors
                except Exception as e:
                    logger.error(f"Unexpected cache invalidation error: {e}", exc_info=True)
                    # Don't fail on cache errors

            return result

        # Store metadata
        wrapper._cache_invalidate_patterns = patterns  # type: ignore[attr-defined]

        return cast(F, wrapper)

    return decorator

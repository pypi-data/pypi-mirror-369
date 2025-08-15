"""Cache package for augint-billing-lib.

Provides a clean caching layer with proper separation of concerns.
"""

import os
from typing import Optional

from .decorators import cache_invalidate, cached
from .lambda_cache import LambdaMemoryCache
from .metrics import CacheMetrics
from .protocol import CacheProtocol

__all__ = [
    "CacheMetrics",
    "CacheProtocol",
    "LambdaMemoryCache",
    "cache_invalidate",
    "cached",
]

# Optional: Global cache instance for backward compatibility
# But prefer dependency injection
_global_cache: Optional[CacheProtocol] = None


def get_global_cache() -> Optional[CacheProtocol]:
    """Get global cache instance."""
    global _global_cache  # noqa: PLW0603
    if _global_cache is None and os.getenv("CACHE_ENABLED", "true").lower() == "true":
        _global_cache = LambdaMemoryCache(
            default_ttl=int(os.getenv("CACHE_DEFAULT_TTL", "300")),
            max_items=int(os.getenv("CACHE_MAX_ITEMS", "1000")),
        )
    return _global_cache


def clear_global_cache() -> None:
    """Clear global cache (mainly for testing)."""
    global _global_cache  # noqa: PLW0603
    if _global_cache:
        _global_cache.clear()
    _global_cache = None  # Reset the instance

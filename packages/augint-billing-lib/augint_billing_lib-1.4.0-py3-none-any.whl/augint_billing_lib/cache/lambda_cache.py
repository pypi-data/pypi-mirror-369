"""Simple memory cache for Lambda containers."""

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .metrics import CacheMetrics


@dataclass
class CacheEntry:
    """A single cache entry."""

    value: Any
    timestamp: float
    ttl: Optional[int]


class LambdaMemoryCache:
    """Simple memory cache optimized for Lambda containers.

    Leverages Lambda container reuse with proper metrics tracking.
    Thread-safe not needed - Lambda handles one request at a time.
    """

    def __init__(self, default_ttl: int = 300, max_items: int = 1000, enabled: bool = True):
        """Initialize cache.

        Args:
            default_ttl: Default TTL in seconds
            max_items: Maximum items before LRU eviction
            enabled: Whether cache is enabled
        """
        self._cache: dict[str, CacheEntry] = {}
        self._access_order: list[str] = []
        self._default_ttl = default_ttl
        self._max_items = max_items
        self._enabled = enabled
        self._metrics = CacheMetrics()
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if not self._enabled or key is None:
            return None

        with self._lock:
            if key not in self._cache:
                self._metrics.misses += 1
                return None

            entry = self._cache[key]
            ttl = entry.ttl if entry.ttl is not None else self._default_ttl

            # Check expiration
            if time.time() - entry.timestamp > ttl:
                del self._cache[key]
                self._access_order.remove(key)
                self._metrics.misses += 1
                return None

            # Update LRU order
            self._access_order.remove(key)
            self._access_order.append(key)

            self._metrics.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        if not self._enabled or key is None or value is None:
            return

        with self._lock:
            try:
                # Check size limit
                if len(self._cache) >= self._max_items and key not in self._cache:
                    # Evict least recently used
                    lru_key = self._access_order[0]
                    del self._cache[lru_key]
                    self._access_order.pop(0)
                    self._metrics.evictions += 1

                # Store entry
                self._cache[key] = CacheEntry(value=value, timestamp=time.time(), ttl=ttl)

                # Update LRU order
                if key in self._access_order:
                    self._access_order.remove(key)
                self._access_order.append(key)

                self._metrics.sets += 1
            except Exception:
                self._metrics.errors += 1
                # Graceful degradation - don't fail the operation

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._enabled:
            return False

        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_order.remove(key)
                self._metrics.deletes += 1
                return True
            return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            # Don't reset metrics - keep historical data

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and cache."""
        value = self.get(key)
        if value is not None:
            return value

        value = factory()
        if value is not None:
            self.set(key, value, ttl)
        return value

    def get_all_keys(self) -> list[str]:
        """Get all cache keys (for pattern matching)."""
        with self._lock:
            return list(self._cache.keys())

    def get_metrics(self) -> dict[str, Any]:
        """Get cache metrics."""
        return self._metrics.to_dict()

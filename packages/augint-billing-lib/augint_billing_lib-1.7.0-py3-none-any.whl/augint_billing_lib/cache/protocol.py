"""Cache protocol and types."""

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class CacheProtocol(Protocol):
    """Protocol that any cache implementation must follow."""

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL."""
        ...

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: int | None = None) -> Any:
        """Get from cache or compute and cache."""
        ...

    def get_all_keys(self) -> list[str]:
        """Get all cache keys (for pattern matching)."""
        ...

    def get_metrics(self) -> dict[str, Any]:
        """Get cache metrics."""
        ...

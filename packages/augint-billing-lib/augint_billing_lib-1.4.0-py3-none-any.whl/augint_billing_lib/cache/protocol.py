"""Cache protocol and types."""

from typing import Any, Callable, Optional, Protocol, runtime_checkable


@runtime_checkable
class CacheProtocol(Protocol):
    """Protocol that any cache implementation must follow."""

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        ...

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        ...

    def clear(self) -> None:
        """Clear all cache entries."""
        ...

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl: Optional[int] = None) -> Any:
        """Get from cache or compute and cache."""
        ...

    def get_all_keys(self) -> list[str]:
        """Get all cache keys (for pattern matching)."""
        ...

    def get_metrics(self) -> dict[str, Any]:
        """Get cache metrics."""
        ...

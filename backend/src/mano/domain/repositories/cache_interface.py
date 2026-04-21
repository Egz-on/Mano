"""Cache interface for dependency injection."""

from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Abstract interface for cache operations."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Get value from cache by key."""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL (time to live in seconds)."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete value from cache by key."""
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        ...

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching a pattern."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close cache connection."""
        ...

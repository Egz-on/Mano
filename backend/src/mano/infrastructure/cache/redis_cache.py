"""Redis cache implementation."""

from __future__ import annotations
import redis.asyncio as aioredis
import json
from typing import Any
from ...domain.repositories.cache_interface import CacheInterface


class RedisCache(CacheInterface):
    """Redis implementation of cache interface."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        """Initialize Redis cache with client."""
        self._client = redis_client

    async def get(self, key: str) -> Any | None:
        """Get value from cache by key."""
        try:
            value = await self._client.get(key)
            if value is None:
                return None
            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception:
            # If Redis is unavailable, return None (graceful degradation)
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL (time to live in seconds)."""
        try:
            # Serialize value to JSON if it's a dict/list, otherwise store as string
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            else:
                serialized = str(value)

            if ttl:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)
        except Exception:
            # If Redis is unavailable, silently fail (graceful degradation)
            pass  # nosec

    async def delete(self, key: str) -> None:
        """Delete value from cache by key."""
        try:
            await self._client.delete(key)
        except Exception:
            # If Redis is unavailable, silently fail
            pass  # nosec

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            result = await self._client.exists(key)
            return bool(result)
        except Exception:
            return False

    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching a pattern."""
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                await self._client.delete(*keys)
        except Exception:
            # If Redis is unavailable, silently fail
            pass  # nosec

    async def close(self) -> None:
        """Close cache connection (client is managed externally)."""
        # Connection is managed by RedisClient singleton
        pass

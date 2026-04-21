"""Redis connection management."""

from __future__ import annotations

import redis.asyncio as aioredis

from workmate.infrastructure.config.settings import get_settings


class RedisClient:
    """Redis client singleton for connection management."""

    _client: aioredis.Redis | None = None
    _settings = get_settings()

    @classmethod
    async def get_client(cls) -> aioredis.Redis:
        """Get or create Redis client instance."""
        if cls._client is None:
            settings = cls._settings.redis
            cls._client = aioredis.from_url(  # type: ignore[no-untyped-call]
                settings.url,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close Redis client connection."""
        if cls._client:
            await cls._client.aclose()
            cls._client = None


# FastAPI dependency
async def get_redis_client() -> aioredis.Redis:
    """FastAPI dependency to get Redis client."""
    return await RedisClient.get_client()


# Global instance for direct access
redis_client = RedisClient()

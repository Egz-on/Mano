"""User domain service implementation."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from workmate.domain.exceptions.base import DomainError, UserNotFoundError
from workmate.domain.models.user import UserAuthId, UserId, UserProfile, UserRole
from workmate.domain.repositories.user_repository import UserRepository


class UserService:
    """User domain service for business logic operations."""

    def __init__(self, user_repository: UserRepository, cache: Any | None = None) -> None:
        self.user_repository = user_repository
        self.cache = cache
        self._cache_ttl = 300

    def _cache_key(self, user_id: UserId | str) -> str:
        return f"user:id:{user_id}"

    def _cache_key_auth(self, auth_user_id: UserAuthId | str) -> str:
        return f"user:auth:{auth_user_id}"

    @staticmethod
    def _from_cached_dict(cached: dict[str, Any]) -> UserProfile:
        return UserProfile(
            id=UserId(cached["id"]),
            auth_user_id=UserAuthId(cached["auth_user_id"]),
            full_name=cached["full_name"],
            phone=cached["phone"],
            avatar_url=cached.get("avatar_url"),
            bio=cached.get("bio"),
            role=UserRole(cached["role"]),
            city=cached.get("city"),
            address=cached.get("address"),
            years_of_experience=cached.get("years_of_experience"),
            company_name=cached.get("company_name"),
            profile_metadata=cached.get("profile_metadata") or {},
            created_at=datetime.fromisoformat(cached["created_at"]),
            updated_at=datetime.fromisoformat(cached["updated_at"]),
            last_login=(datetime.fromisoformat(cached["last_login"]) if cached.get("last_login") else None),
            total_services=cached.get("total_services", 0),
            average_rating=cached.get("average_rating", 0.0),
            total_reviews=cached.get("total_reviews", 0),
        )

    async def create_user_profile(self, user: UserProfile) -> UserProfile:
        existing = await self.user_repository.get_user_by_auth_user_id(user.auth_user_id)
        if existing:
            raise DomainError(f"User with auth ID {user.auth_user_id} already exists")

        if not user.has_complete_profile():
            raise DomainError("Profile must have full_name and phone")
        if user.is_provider() and not user.company_name:
            raise DomainError("Providers must provide company name")

        created_user = await self.user_repository.create_user_profile(user)

        if self.cache:
            payload = json.dumps(created_user.to_dict())
            await self.cache.set(self._cache_key(created_user.id), payload, ex=self._cache_ttl)
            await self.cache.set(self._cache_key_auth(created_user.auth_user_id), payload, ex=self._cache_ttl)

        return created_user

    async def get_user_by_id(self, user_id: UserId) -> UserProfile:
        key = self._cache_key(user_id)
        if self.cache:
            raw_cached = await self.cache.get(key)
            if raw_cached:
                return self._from_cached_dict(json.loads(raw_cached))

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        if self.cache:
            payload = json.dumps(user.to_dict())
            await self.cache.set(key, payload, ex=self._cache_ttl)
            await self.cache.set(self._cache_key_auth(user.auth_user_id), payload, ex=self._cache_ttl)

        return user

    async def get_user_by_auth_user_id(self, auth_user_id: UserAuthId) -> UserProfile:
        key = self._cache_key_auth(auth_user_id)
        if self.cache:
            raw_cached = await self.cache.get(key)
            if raw_cached:
                return self._from_cached_dict(json.loads(raw_cached))

        user = await self.user_repository.get_user_by_auth_user_id(auth_user_id)
        if not user:
            raise UserNotFoundError(f"User {auth_user_id} not found")

        if self.cache:
            payload = json.dumps(user.to_dict())
            await self.cache.set(key, payload, ex=self._cache_ttl)
            await self.cache.set(self._cache_key(user.id), payload, ex=self._cache_ttl)

        return user

    async def update_user_profile(self, user: UserProfile) -> UserProfile:
        result = await self.user_repository.update_user(user)

        if self.cache:
            payload = json.dumps(result.to_dict())
            await self.cache.delete(self._cache_key(user.id))
            await self.cache.delete(self._cache_key_auth(user.auth_user_id))
            await self.cache.set(self._cache_key(result.id), payload, ex=self._cache_ttl)
            await self.cache.set(self._cache_key_auth(result.auth_user_id), payload, ex=self._cache_ttl)

        return result

    async def delete_user(self, user_id: UserId) -> None:
        await self.user_repository.delete_user(user_id)

    async def list_users(self) -> list[UserProfile]:
        return await self.user_repository.list_users()

    async def recalculate_user_stats(self, auth_user_id: UserAuthId) -> UserProfile:
        user = await self.get_user_by_auth_user_id(auth_user_id)
        stats = await self.user_repository.get_user_stats(user.id)
        updated_user = user.update_stats(
            total_services=stats["total_services"],
            average_rating=stats["average_rating"],
            total_reviews=stats["total_reviews"],
        )
        result = await self.user_repository.update_user(updated_user)

        if self.cache:
            payload = json.dumps(result.to_dict())
            await self.cache.delete(self._cache_key(user.id))
            await self.cache.delete(self._cache_key_auth(auth_user_id))
            await self.cache.set(self._cache_key(result.id), payload, ex=self._cache_ttl)
            await self.cache.set(self._cache_key_auth(auth_user_id), payload, ex=self._cache_ttl)

        return result

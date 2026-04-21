"""User repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from workmate.domain.models.user import UserAuthId, UserId, UserProfile


class UserRepository(ABC):
    """Abstract base class for user repository."""

    @abstractmethod
    async def create_user_profile(self, user: UserProfile) -> UserProfile:
        """Create a new user profile."""

    @abstractmethod
    async def get_user_by_id(self, user_id: UserId) -> UserProfile | None:
        """Get user by internal ID."""

    @abstractmethod
    async def get_user_by_auth_user_id(self, auth_user_id: UserAuthId) -> UserProfile | None:
        """Get user by auth-system ID."""

    @abstractmethod
    async def update_user(self, user: UserProfile) -> UserProfile:
        """Update an existing user."""

    @abstractmethod
    async def delete_user(self, user_id: UserId) -> None:
        """Delete a user."""

    @abstractmethod
    async def list_users(self) -> list[UserProfile]:
        """List all users."""

    @abstractmethod
    async def get_user_stats(self, user_id: UserId) -> dict[str, Any]:
        """Get user statistics such as total services and ratings."""

"""User DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from workmate.domain.models.user import UserProfile, UserRole


@dataclass(frozen=True)
class CreateUserRequest:
    """DTO for creating a user profile."""

    auth_user_id: UUID
    full_name: str
    phone: str
    avatar_url: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.client
    city: str | None = None
    address: str | None = None
    years_of_experience: int | None = None
    company_name: str | None = None
    profile_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateUserRequest:
    """DTO for updating user profile."""

    full_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    city: str | None = None
    address: str | None = None
    role: UserRole | None = None
    years_of_experience: int | None = None
    company_name: str | None = None
    profile_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UserResponse:
    """DTO for user profile response."""

    id: UUID
    auth_user_id: UUID
    full_name: str
    phone: str
    avatar_url: str | None
    bio: str | None
    role: UserRole
    city: str | None
    address: str | None
    years_of_experience: int | None
    company_name: str | None
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None

    @classmethod
    def from_domain(cls, user: UserProfile) -> "UserResponse":
        return cls(
            id=UUID(user.id.value),
            auth_user_id=UUID(user.auth_user_id.value),
            full_name=user.full_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role,
            city=user.city,
            address=user.address,
            years_of_experience=user.years_of_experience,
            company_name=user.company_name,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )

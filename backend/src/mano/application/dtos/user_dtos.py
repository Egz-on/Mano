"""User DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from mano.domain.models.user import UserProfile, UserRole


@dataclass(frozen=True)
class CreateUserRequest:
    """DTO for creating a user profile."""

    auth_user_id: UUID
    name: str
    surname: str
    phone: str
    avatar_url: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.client
    city: str | None = None
    address: str | None = None
    years_of_experience: int | None = None
    company_name: str | None = None
    is_active: bool = True
    is_online: bool = False
    latitude: float | None = None
    longitude: float | None = None
    approval_status: str = "pending"
    fcm_token: str | None = None
    profile_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UpdateUserRequest:
    """DTO for updating user profile."""

    name: str | None = None
    surname: str | None = None
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    city: str | None = None
    address: str | None = None
    role: UserRole | None = None
    years_of_experience: int | None = None
    company_name: str | None = None
    is_active: bool | None = None
    is_online: bool | None = None
    latitude: float | None = None
    longitude: float | None = None
    approval_status: str | None = None
    fcm_token: str | None = None
    profile_metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class UserResponse:
    """DTO for user profile response."""

    id: UUID
    auth_user_id: UUID
    name: str
    surname: str
    phone: str
    avatar_url: str | None
    bio: str | None
    role: UserRole
    city: str | None
    address: str | None
    years_of_experience: int | None
    company_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None
    is_online: bool
    latitude: float | None
    longitude: float | None
    approval_status: str
    fcm_token: str | None

    @classmethod
    def from_domain(cls, user: UserProfile) -> UserResponse:
        return cls(
            id=UUID(user.id.value),
            auth_user_id=UUID(user.auth_user_id.value),
            name=user.name,
            surname=user.surname,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=user.role,
            city=user.city,
            address=user.address,
            years_of_experience=user.years_of_experience,
            company_name=user.company_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            is_online=user.is_online,
            latitude=user.latitude,
            longitude=user.longitude,
            approval_status=user.approval_status,
            fcm_token=user.fcm_token,
        )

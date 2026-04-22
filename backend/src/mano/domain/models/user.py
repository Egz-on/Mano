# Domain Layer - User Model
"""User domain entities and value objects."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
import uuid


class UserRole(StrEnum):
    """User role value object."""

    admin = "admin"
    provider = "provider"
    client = "client"


@dataclass(frozen=True)
class PhoneNumber:
    """Phone number value object with validation."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("+389"):
            raise ValueError("Phone must start with +389")
        if len(self.value) != 12:
            raise ValueError("Phone must be 12 characters (+38970123456)")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserId:
    """Internal user identifier."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserAuthId:
    """Authentication-system user identifier."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class UserProfile:
    """Immutable user profile entity."""

    id: UserId
    auth_user_id: UserAuthId
    name: str
    phone: str
    surname: str = ""
    avatar_url: str | None = None
    bio: str | None = None
    role: UserRole = UserRole.client
    city: str | None = None
    address: str | None = None
    years_of_experience: int | None = None
    company_name: str | None = None
    is_active: bool = True
    profile_metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = None
    is_online: bool = False
    latitude: float | None = None
    longitude: float | None = None
    approval_status: str = "pending"
    fcm_token: str | None = None
    total_services: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_surname = self.surname.strip()
        if not normalized_name:
            raise ValueError("Name cannot be empty")
        if not self.phone.strip():
            raise ValueError("Phone cannot be empty")
        if self.years_of_experience is not None and self.years_of_experience < 0:
            raise ValueError("Years of experience cannot be negative")
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if not self.approval_status.strip():
            raise ValueError("Approval status cannot be empty")
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "surname", normalized_surname)
        object.__setattr__(self, "approval_status", self.approval_status.strip())

    @property
    def full_name(self) -> str:
        return " ".join(part for part in [self.name, self.surname] if part)

    def is_provider(self) -> bool:
        return self.role == UserRole.provider

    def is_client(self) -> bool:
        return self.role == UserRole.client

    def is_admin(self) -> bool:
        return self.role == UserRole.admin

    def has_complete_profile(self) -> bool:
        return bool(self.name.strip() and self.phone.strip())

    def get_display_name(self) -> str:
        if self.company_name and self.is_provider():
            return self.company_name
        return self.full_name

    def update_last_login(self) -> UserProfile:
        return replace(self, last_login=datetime.now(UTC), updated_at=datetime.now(UTC))

    def update_profile(
        self,
        name: str | None = None,
        surname: str | None = None,
        phone: str | None = None,
        avatar_url: str | None = None,
        bio: str | None = None,
        city: str | None = None,
        address: str | None = None,
        years_of_experience: int | None = None,
        company_name: str | None = None,
        is_active: bool | None = None,
        is_online: bool | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        approval_status: str | None = None,
        fcm_token: str | None = None,
    ) -> UserProfile:
        updates: dict[str, Any] = {"updated_at": datetime.now(UTC)}

        if name is not None:
            updates["name"] = name
        if surname is not None:
            updates["surname"] = surname
        if phone is not None:
            updates["phone"] = phone
        if avatar_url is not None:
            updates["avatar_url"] = avatar_url
        if bio is not None:
            updates["bio"] = bio
        if city is not None:
            updates["city"] = city
        if address is not None:
            updates["address"] = address
        if years_of_experience is not None:
            updates["years_of_experience"] = years_of_experience
        if company_name is not None:
            updates["company_name"] = company_name
        if is_active is not None:
            updates["is_active"] = is_active
        if is_online is not None:
            updates["is_online"] = is_online
        if latitude is not None:
            updates["latitude"] = latitude
        if longitude is not None:
            updates["longitude"] = longitude
        if approval_status is not None:
            updates["approval_status"] = approval_status
        if fcm_token is not None:
            updates["fcm_token"] = fcm_token

        return replace(self, **updates)

    def change_role(self, role: UserRole) -> UserProfile:
        """Return a new profile with an updated role."""
        return replace(self, role=role, updated_at=datetime.now(UTC))

    def replace_profile_metadata(self, profile_metadata: dict[str, Any]) -> UserProfile:
        """Return a new profile with replaced metadata."""
        return replace(self, profile_metadata=profile_metadata, updated_at=datetime.now(UTC))

    def update_stats(self, total_services: int, average_rating: float, total_reviews: int) -> UserProfile:
        return replace(self, total_services=total_services, average_rating=average_rating, total_reviews=total_reviews)

    def to_dict(self) -> dict[str, Any]:
        auth_user_id = str(self.auth_user_id)
        return {
            "id": str(self.id),
            "auth_user_id": auth_user_id,
            "name": self.name,
            "surname": self.surname,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "role": str(self.role),
            "city": self.city,
            "address": self.address,
            "years_of_experience": self.years_of_experience,
            "company_name": self.company_name,
            "is_active": self.is_active,
            "profile_metadata": self.profile_metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_online": self.is_online,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "approval_status": self.approval_status,
            "fcm_token": self.fcm_token,
            "total_services": self.total_services,
            "average_rating": self.average_rating,
            "total_reviews": self.total_reviews,
        }

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, name={self.full_name}, role={self.role})>"

"""Service domain entities and value types."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
import uuid

from mano.domain.exceptions.base import DomainError


@dataclass(frozen=True)
class ServiceId:
    """Service identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of ServiceId."""
        return self.value


@dataclass(frozen=True)
class ProviderId:
    """Provider identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of ProviderId."""
        return self.value


@dataclass(frozen=True)
class CategoryId:
    """Category identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of CategoryId."""
        return self.value


@dataclass(frozen=True)
class ServiceImage:
    """Value Object për imazhet e shërbimit"""

    url: str
    public_id: str
    width: int | None = None
    height: int | None = None
    format: str | None = None
    thumbnail_url: str | None = None


class PricingType(StrEnum):
    """Supported service pricing modes."""

    fixed = "fixed"
    hourly = "hourly"
    daily = "daily"
    custom = "custom"


@dataclass(frozen=True)
class Service:
    """
    Service Domain Entity
    Represents a service offered by a provider
    """

    # Identity
    id: ServiceId
    provider_id: ProviderId
    category_id: CategoryId

    # Basic Info
    title: str
    description: str

    # Pricing
    price: float
    currency: str = "MKD"
    pricing_type: str = PricingType.fixed.value

    # Location & Metadata
    service_areas: list[str] = field(default_factory=list)
    service_metadata: dict[str, Any] = field(default_factory=dict)
    images: list[str] = field(default_factory=list)

    # Stats (calculated - not persisted)
    rating: float = field(default=0.0, repr=False)
    review_count: int = field(default=0, repr=False)

    # Status
    is_active: bool = True
    is_featured: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        title = self.title.strip()
        description = self.description.strip()
        if not title:
            raise DomainError("Service title is required")
        if len(title) > 255:
            raise DomainError("Service title must be 255 characters or less")
        if not description:
            raise DomainError("Service description is required")
        if len(description) < 10:
            raise DomainError("Service description must be at least 10 characters long")
        if self.price <= 0:
            raise DomainError("Service price must be greater than zero")

        currency = self.currency.strip().upper()
        if len(currency) != 3 or not currency.isalpha():
            raise DomainError("Currency must be a 3-letter code (e.g., MKD, USD)")

        pricing_type = PricingType(self.pricing_type).value
        service_areas = [area.strip() for area in self.service_areas if area.strip()]
        if self.service_areas and not service_areas:
            raise DomainError("Service areas cannot contain only blank values")

        object.__setattr__(self, "title", title)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "currency", currency)
        object.__setattr__(self, "pricing_type", pricing_type)
        object.__setattr__(self, "service_areas", service_areas)

    @classmethod
    def create(
        cls,
        *,
        provider_id: ProviderId,
        category_id: CategoryId,
        title: str,
        description: str,
        price: float,
        currency: str = "MKD",
        pricing_type: str = PricingType.fixed.value,
        service_areas: list[str] | None = None,
        service_metadata: dict[str, Any] | None = None,
        images: list[str] | None = None,
        is_active: bool = True,
        is_featured: bool = False,
    ) -> Service:
        """Create a normalized service entity."""
        now = datetime.now(UTC)
        return cls(
            id=ServiceId(),
            provider_id=provider_id,
            category_id=category_id,
            title=title,
            description=description,
            price=price,
            currency=currency,
            pricing_type=pricing_type,
            service_areas=service_areas or [],
            service_metadata=service_metadata or {},
            images=images or [],
            is_active=is_active,
            is_featured=is_featured,
            created_at=now,
            updated_at=now,
        )

    def active(self) -> Service:
        """Activate the service."""
        return replace(self, is_active=True, updated_at=datetime.now(UTC))

    def deactive(self) -> Service:
        """Deactivate the service."""
        return replace(self, is_active=False, updated_at=datetime.now(UTC))

    def update_description(self, new_description: str) -> Service:
        """Update the service description."""
        return replace(self, description=new_description, updated_at=datetime.now(UTC))

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        price: float | None = None,
        currency: str | None = None,
        pricing_type: str | None = None,
        service_areas: list[str] | None = None,
        service_metadata: dict[str, Any] | None = None,
        images: list[str] | None = None,
        is_active: bool | None = None,
        is_featured: bool | None = None,
    ) -> Service:
        """Update service details."""
        return replace(
            self,
            title=title if title is not None else self.title,
            description=description if description is not None else self.description,
            price=price if price is not None else self.price,
            currency=currency if currency is not None else self.currency,
            pricing_type=pricing_type if pricing_type is not None else self.pricing_type,
            service_areas=service_areas if service_areas is not None else self.service_areas,
            service_metadata=service_metadata if service_metadata is not None else self.service_metadata,
            images=images if images is not None else self.images,
            is_active=is_active if is_active is not None else self.is_active,
            is_featured=is_featured if is_featured is not None else self.is_featured,
            updated_at=datetime.now(UTC),
        )

    def update_stats(self, rating: float, review_count: int) -> Service:
        """Update service statistics."""
        return replace(
            self,
            rating=rating,
            review_count=review_count,
            updated_at=datetime.now(UTC),
        )

    def mark_as_featured(self) -> Service:
        """Mark the service as featured."""
        return replace(self, is_featured=True, updated_at=datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": str(self.id),
            "provider_id": str(self.provider_id),
            "category_id": str(self.category_id),
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "currency": self.currency,
            "pricing_type": self.pricing_type,
            "service_areas": self.service_areas,
            "service_metadata": self.service_metadata,
            "images": self.images,
            "rating": self.rating,
            "review_count": self.review_count,
            "is_active": self.is_active,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, title={self.title}, price={self.price} {self.currency})>"

"""Service Domain Entity"""

from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any
import uuid


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
    currency: str = "MKD"  # Macedonian Denar
    pricing_type: str = "fixed"  # fixed, hourly, daily, custom

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
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def active(self) -> "Service":
        """Active the service.""" ""
        return replace(self, is_active=True, updated_at=datetime.now())

    def deactive(self) -> "Service":
        """Deactive the service.""" ""
        return replace(self, is_active=False, updated_at=datetime.now())

    def update_description(self, new_description: str) -> "Service":
        """Update the service description."""
        if not new_description or len(new_description) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return replace(self, description=new_description, updated_at=datetime.now())

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
    ) -> "Service":
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
            updated_at=datetime.now(),
        )

    def update_stats(self, rating: float, review_count: int) -> "Service":
        """Update service statistics."""
        return replace(
            self,
            rating=rating,
            review_count=review_count,
            updated_at=datetime.now(),
        )

    def mark_as_featured(self) -> "Service":
        """Mark the service as featured."""
        return replace(self, is_featured=True, updated_at=datetime.now())

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

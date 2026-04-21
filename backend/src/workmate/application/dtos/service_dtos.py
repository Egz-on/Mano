"""Application Layer DTOs - Internal Data Transfer Objects
Simple data containers without validation logic
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Any
from workmate.domain.models.service_model import ServiceId, ProviderId, CategoryId, Service


@dataclass(frozen=True)
class CreateServiceRequest:
    """DTO for creating a service."""

    provider_id: ProviderId
    category_id: CategoryId
    title: str
    description: str
    price: float
    currency: str = "MKD"
    pricing_type: str = "fixed"


@dataclass(frozen=True)
class UpdateServiceRequest:
    """DTO for updating a service."""

    title: str | None = None
    description: str | None = None
    price: float | None = None
    currency: str | None = None
    pricing_type: str | None = None
    service_areas: list[str] | None = None
    service_metadata: dict[str, Any] | None = None
    images: list[str] | None = None
    is_active: bool | None = None
    is_featured: bool | None = None


# ============================================
# FILTER DTOs
# ============================================


@dataclass(frozen=True)
class ServiceResponseDTO:
    """DTO for service response."""

    id: ServiceId
    provider_id: ProviderId
    category_id: CategoryId
    title: str
    description: str
    price: float
    currency: str
    pricing_type: str
    service_areas: list[str]
    service_metadata: dict[str, Any]
    images: list[str]
    rating: float
    review_count: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, service: Service) -> "ServiceResponseDTO":
        """Convert domain Service to ServiceResponseDTO."""
        return cls(
            id=service.id,
            provider_id=service.provider_id,
            category_id=service.category_id,
            title=service.title,
            description=service.description,
            price=service.price,
            currency=service.currency,
            pricing_type=service.pricing_type,
            service_areas=service.service_areas,
            service_metadata=service.service_metadata,
            images=service.images,
            rating=service.rating,
            review_count=service.review_count,
            is_active=service.is_active,
            is_featured=service.is_featured,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )


@dataclass(frozen=True)
class ServiceFilterDTO:
    """DTO for filtering services."""

    provider_id: ProviderId | None = None
    category_id: CategoryId | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    min_price: float | None = None
    max_price: float | None = None

    model_config = {"from_attributes": True}


@dataclass(frozen=True)
class ServiceImageDTO:
    """DTO for service images."""

    url: str
    public_id: str
    width: int | None = None
    height: int | None = None
    format: str | None = None
    thumbnail_url: str | None = None

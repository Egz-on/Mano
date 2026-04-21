"""
Service Schema Definitions
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Any


class CreateServiceSchema(BaseModel):
    """Schema for creating a new service."""

    provider_id: UUID = Field(..., description="ID of the service provider")
    category_id: UUID = Field(..., description="ID of the service category")
    title: str = Field(..., description="Title of the service")
    description: str = Field(..., description="Detailed description of the service")
    price: float = Field(..., description="Price of the service")
    currency: str = Field(default="MKD", description="Currency of the price")
    pricing_type: str = Field(..., description="Pricing type of the service")
    service_areas: list[str] = Field(..., description="Areas where the service is available")
    service_metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the service")
    images: list[str] = Field(default_factory=list, description="List of image URLs for the service")
    is_active: bool = Field(default=True, description="Whether the service is active")
    is_featured: bool = Field(default=False, description="Whether the service is featured")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the service was created")
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp when the service was last updated"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Professional Plumbing Service",
                "description": "We offer top-notch plumbing services for residential and commercial properties.",
                "price": 150.0,
                "currency": "MKD",
                "pricing_type": "fixed",
                "service_areas": ["Tetov", "Xhepchisht"],
                "service_metadata": {"emergency_service": True},
                "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"],
                "is_active": True,
                "is_featured": False,
            }
        }
    }


class ServiceResponseSchema(BaseModel):
    """Schema for service response."""

    id: UUID = Field(..., description="Unique identifier of the service")
    provider_id: UUID = Field(..., description="ID of the service provider")
    category_id: UUID = Field(..., description="ID of the service category")
    title: str = Field(..., description="Title of the service")
    description: str = Field(..., description="Detailed description of the service")
    price: float = Field(..., description="Price of the service")
    currency: str = Field(..., description="Currency of the price")
    pricing_type: str = Field(..., description="Pricing type of the service")
    service_areas: list[str] = Field(..., description="Areas where the service is available")
    service_metadata: dict[str, Any] = Field(..., description="Additional metadata for the service")
    images: list[str] = Field(..., description="List of image URLs for the service")
    rating: float = Field(..., description="Average rating of the service")
    review_count: int = Field(..., description="Number of reviews for the service")
    is_active: bool = Field(..., description="Whether the service is active")
    is_featured: bool = Field(..., description="Whether the service is featured")
    created_at: datetime = Field(..., description="Timestamp when the service was created")
    updated_at: datetime = Field(..., description="Timestamp when the service was last updated")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "provider_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "Professional Plumbing Service",
                "description": "We offer top-notch plumbing services for residential and commercial properties.",
                "price": 150.0,
                "currency": "MKD",
                "pricing_type": "fixed",
                "service_areas": ["Tetov", "Xhepchisht"],
                "service_metadata": {"emergency_service": True},
                "images": ["http://example.com/image1.jpg", "http://example.com/image2.jpg"],
                "rating": 4.5,
                "review_count": 25,
                "is_active": True,
                "is_featured": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T12:00:00Z",
            }
        }
    }


class UpdateServiceSchema(BaseModel):
    """Schema for updating a service."""

    title: str | None = Field(None, description="Title of the service")
    description: str | None = Field(None, description="Detailed description of the service")
    price: float | None = Field(None, description="Price of the service")
    currency: str | None = Field(None, description="Currency of the price")
    pricing_type: str | None = Field(None, description="Pricing type of the service")
    service_areas: list[str] | None = Field(None, description="Areas where the service is available")
    service_metadata: dict[str, Any] | None = Field(None, description="Additional metadata for the service")
    images: list[str] | None = Field(None, description="List of image URLs for the service")
    is_active: bool | None = Field(None, description="Whether the service is active")
    is_featured: bool | None = Field(None, description="Whether the service is featured")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Updated Plumbing Service",
                "description": "Updated description for plumbing services.",
                "price": 175.0,
                "currency": "MKD",
                "pricing_type": "fixed",
                "service_areas": ["Tetov", "Gostivar"],
                "service_metadata": {"emergency_service": False},
                "images": ["http://example.com/newimage1.jpg"],
                "is_active": True,
                "is_featured": True,
            }
        }
    }

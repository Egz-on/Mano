"""
Category Schema Definitions
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateCategorySchema(BaseModel):
    """Schema for creating a new category."""

    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    icon: str | None = Field(None, description="Icon name or URL")
    description: str | None = Field(None, description="Category description")
    parent_id: UUID | None = Field(None, description="Parent category ID")
    is_active: bool = Field(default=True, description="Whether the category is active")
    display_order: int = Field(default=0, description="Display order")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Plumbing",
                "slug": "plumbing",
                "icon": "wrench",
                "description": "All plumbing related services",
                "parent_id": None,
                "is_active": True,
                "display_order": 1,
            }
        }
    }


class UpdateCategorySchema(BaseModel):
    """Schema for updating a category."""

    name: str | None = Field(None, description="Category name")
    slug: str | None = Field(None, description="URL-friendly slug")
    icon: str | None = Field(None, description="Icon name or URL")
    description: str | None = Field(None, description="Category description")
    parent_id: UUID | None = Field(None, description="Parent category ID")
    is_active: bool | None = Field(None, description="Whether the category is active")
    display_order: int | None = Field(None, description="Display order")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Home Plumbing",
                "slug": "home-plumbing",
                "icon": "pipe",
                "description": "Residential plumbing services",
                "parent_id": None,
                "is_active": True,
                "display_order": 2,
            }
        }
    }


class CategoryResponseSchema(BaseModel):
    """Schema for category response."""

    id: UUID = Field(..., description="Unique identifier of the category")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    icon: str | None = Field(None, description="Icon name or URL")
    description: str | None = Field(None, description="Category description")
    parent_id: UUID | None = Field(None, description="Parent category ID")
    is_active: bool = Field(..., description="Whether the category is active")
    display_order: int = Field(..., description="Display order")
    created_at: datetime = Field(..., description="Timestamp when the category was created")
    updated_at: datetime = Field(..., description="Timestamp when the category was last updated")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174010",
                "name": "Plumbing",
                "slug": "plumbing",
                "icon": "wrench",
                "description": "All plumbing related services",
                "parent_id": None,
                "is_active": True,
                "display_order": 1,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-10T12:00:00Z",
            }
        }
    }

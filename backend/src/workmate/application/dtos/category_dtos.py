"""Category DTOs for application layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from workmate.domain.models.category import Category, CategoryId


@dataclass(frozen=True)
class CreateCategoryRequest:
    """DTO for creating a category."""

    name: str
    slug: str
    icon: str | None = None
    description: str | None = None
    parent_id: CategoryId | None = None
    is_active: bool = True
    display_order: int = 0


@dataclass(frozen=True)
class UpdateCategoryRequest:
    """DTO for updating a category."""

    name: str | None = None
    slug: str | None = None
    icon: str | None = None
    description: str | None = None
    parent_id: CategoryId | None = None
    is_active: bool | None = None
    display_order: int | None = None


@dataclass(frozen=True)
class CategoryResponseDTO:
    """DTO for category response."""

    id: CategoryId
    name: str
    slug: str
    icon: str | None
    description: str | None
    parent_id: CategoryId | None
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, category: Category) -> CategoryResponseDTO:
        """Convert domain Category to CategoryResponseDTO."""
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            icon=category.icon,
            description=category.description,
            parent_id=category.parent_id,
            is_active=category.is_active,
            display_order=category.display_order,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

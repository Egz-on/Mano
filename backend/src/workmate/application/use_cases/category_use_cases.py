"""Category use cases."""

from __future__ import annotations

from datetime import datetime, UTC
from workmate.domain.models.category import Category, CategoryId
from workmate.domain.services.category_service import CategoryService
from workmate.application.dtos.category_dtos import (
    CategoryResponseDTO,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)


class CategoryUseCases:
    """Category use cases."""

    def __init__(self, category_service: CategoryService):
        """Initialize category use cases."""
        self.category_service = category_service

    async def create_category(self, request: CreateCategoryRequest) -> CategoryResponseDTO:
        """Create a new category."""
        category = Category(
            id=CategoryId(),
            name=request.name,
            slug=request.slug,
            icon=request.icon,
            description=request.description,
            parent_id=request.parent_id,
            is_active=request.is_active,
            display_order=request.display_order,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        created = await self.category_service.create_category(category)
        return CategoryResponseDTO.from_domain(created)

    async def get_category_by_id(self, category_id: str) -> CategoryResponseDTO:
        """Get category by ID."""
        category = await self.category_service.get_category_by_id(CategoryId(category_id))
        return CategoryResponseDTO.from_domain(category)

    async def get_category_by_slug(self, slug: str) -> CategoryResponseDTO:
        """Get category by slug."""
        category = await self.category_service.get_category_by_slug(slug)
        return CategoryResponseDTO.from_domain(category)

    async def list_categories(self) -> list[CategoryResponseDTO]:
        """List categories."""
        categories = await self.category_service.list_categories()
        return [CategoryResponseDTO.from_domain(c) for c in categories]

    async def update_category(self, category_id: str, request: UpdateCategoryRequest) -> CategoryResponseDTO:
        """Update an existing category."""
        category = await self.category_service.get_category_by_id(CategoryId(category_id))
        updated = Category(
            id=category.id,
            name=request.name if request.name is not None else category.name,
            slug=request.slug if request.slug is not None else category.slug,
            icon=request.icon if request.icon is not None else category.icon,
            description=request.description if request.description is not None else category.description,
            parent_id=request.parent_id if request.parent_id is not None else category.parent_id,
            is_active=request.is_active if request.is_active is not None else category.is_active,
            display_order=request.display_order if request.display_order is not None else category.display_order,
            created_at=category.created_at,
            updated_at=datetime.now(UTC),
        )
        saved = await self.category_service.update_category(updated)
        return CategoryResponseDTO.from_domain(saved)

    async def delete_category(self, category_id: str) -> None:
        """Delete category by ID."""
        await self.category_service.delete_category(CategoryId(category_id))

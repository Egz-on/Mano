"""Category domain service implementation."""

from __future__ import annotations
from workmate.domain.repositories.category_repository import CategoryRepository
from workmate.domain.models.category import Category, CategoryId
from workmate.domain.exceptions.base import CategoryAlreadyExistsError, CategoryNotFoundError


class CategoryService:
    """Category domain service for business logic operations."""

    def __init__(self, category_repository: CategoryRepository):
        """Initialize category service."""
        self.category_repository = category_repository

    async def create_category(self, category: Category) -> Category:
        """Create a new category."""
        existing = await self.category_repository.get_category_by_slug(category.slug)
        if existing:
            raise CategoryAlreadyExistsError(f"Category with slug '{category.slug}' already exists")
        return await self.category_repository.create_category(category)

    async def get_category_by_id(self, category_id: CategoryId) -> Category:
        """Get category by ID."""
        category = await self.category_repository.get_category_by_id(category_id)
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return category

    async def get_category_by_slug(self, slug: str) -> Category:
        """Get category by slug."""
        category = await self.category_repository.get_category_by_slug(slug)
        if not category:
            raise CategoryNotFoundError(f"Category slug '{slug}' not found")
        return category

    async def list_categories(self) -> list[Category]:
        """List categories."""
        return await self.category_repository.list_categories()

    async def update_category(self, category: Category) -> Category:
        """Update a category."""
        return await self.category_repository.update_category(category)

    async def delete_category(self, category_id: CategoryId) -> None:
        """Delete category by ID."""
        await self.category_repository.delete_category(category_id)

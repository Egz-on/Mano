from __future__ import annotations
from abc import ABC, abstractmethod
from workmate.domain.models.category import Category, CategoryId


class CategoryRepository(ABC):
    """Abstract base class for Category repository."""

    @abstractmethod
    async def create_category(self, category: Category) -> Category:
        """Create a new category."""
        ...

    @abstractmethod
    async def get_category_by_id(self, category_id: CategoryId) -> Category | None:
        """Get category by ID."""
        ...

    @abstractmethod
    async def get_category_by_slug(self, slug: str) -> Category | None:
        """Get category by slug."""
        ...

    @abstractmethod
    async def list_categories(self) -> list[Category]:
        """List all categories."""
        ...

    @abstractmethod
    async def update_category(self, category: Category) -> Category:
        """Update a category."""
        ...

    @abstractmethod
    async def delete_category(self, category_id: CategoryId) -> None:
        """Delete a category."""
        ...

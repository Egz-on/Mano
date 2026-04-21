"""SQLAlchemy implementation of CategoryRepository for DDD architecture."""

from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from workmate.common.uuid_utils import uuid_to_str
from workmate.domain.models.category import Category, CategoryId
from workmate.domain.repositories.category_repository import CategoryRepository
from workmate.infrastructure.database.models import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    """SQLAlchemy implementation of the CategoryRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    @staticmethod
    def _to_domain(model: CategoryModel) -> Category:
        """Convert database model to domain entity."""
        parent_id = CategoryId(str(model.parent_id)) if model.parent_id else None
        return Category(
            id=CategoryId(str(model.id)),
            name=model.name,
            slug=model.slug,
            icon=model.icon,
            description=model.description,
            parent_id=parent_id,
            is_active=model.is_active,
            display_order=model.display_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _apply_domain_to_model(domain: Category, model: CategoryModel) -> None:
        """Apply domain model changes to database model."""
        model.name = domain.name
        model.slug = domain.slug
        model.icon = domain.icon
        model.description = domain.description
        model.parent_id = uuid_to_str(domain.parent_id) if domain.parent_id else None
        model.is_active = domain.is_active
        model.display_order = domain.display_order
        model.updated_at = domain.updated_at

    async def create_category(self, category: Category) -> Category:
        """Create a new category."""
        model = CategoryModel(
            id=uuid_to_str(category.id),
            name=category.name,
            slug=category.slug,
            icon=category.icon,
            description=category.description,
            parent_id=uuid_to_str(category.parent_id) if category.parent_id else None,
            is_active=category.is_active,
            display_order=category.display_order,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_category_by_id(self, category_id: CategoryId) -> Category | None:
        """Get category by ID."""
        stmt = select(CategoryModel).where(CategoryModel.id == uuid_to_str(category_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_category_by_slug(self, slug: str) -> Category | None:
        """Get category by slug."""
        stmt = select(CategoryModel).where(CategoryModel.slug == slug)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_categories(self) -> list[Category]:
        """List all categories."""
        stmt = select(CategoryModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def update_category(self, category: Category) -> Category:
        """Update an existing category."""
        stmt = select(CategoryModel).where(CategoryModel.id == uuid_to_str(category.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Category with ID {category.id} not found.")

        self._apply_domain_to_model(category, model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete_category(self, category_id: CategoryId) -> None:
        """Delete a category by ID."""
        stmt = delete(CategoryModel).where(CategoryModel.id == uuid_to_str(category_id))
        await self._session.execute(stmt)

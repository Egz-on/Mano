import pytest
from unittest.mock import AsyncMock

from mano.domain.exceptions.base import CategoryAlreadyExistsError, CategoryNotFoundError
from mano.domain.models.category import Category, CategoryId
from mano.domain.repositories.category_repository import CategoryRepository
from mano.domain.services.category_service import CategoryService
from datetime import datetime, UTC


class TestCategoryService:
    @pytest.mark.asyncio
    async def test_create_category(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)

        category = Category(
            id=CategoryId(),
            name="Plumbing",
            slug="plumbing",
            icon=None,
            description=None,
            parent_id=None,
            is_active=True,
            display_order=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_repo.get_category_by_slug.return_value = None
        mock_repo.create_category.return_value = category

        result = await service.create_category(category)

        mock_repo.get_category_by_slug.assert_called_once_with("plumbing")
        mock_repo.create_category.assert_called_once_with(category)
        assert result == category

    @pytest.mark.asyncio
    async def test_create_category_already_exists(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)

        category = Category(
            id=CategoryId(),
            name="Plumbing",
            slug="plumbing",
            icon=None,
            description=None,
            parent_id=None,
            is_active=True,
            display_order=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        mock_repo.get_category_by_slug.return_value = category

        with pytest.raises(CategoryAlreadyExistsError):
            await service.create_category(category)

    @pytest.mark.asyncio
    async def test_get_category_by_id(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        category_id = CategoryId()
        expected = AsyncMock(spec=Category)
        mock_repo.get_category_by_id.return_value = expected

        result = await service.get_category_by_id(category_id)

        mock_repo.get_category_by_id.assert_called_once_with(category_id)
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_category_by_id_not_found(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        category_id = CategoryId()
        mock_repo.get_category_by_id.return_value = None

        with pytest.raises(CategoryNotFoundError):
            await service.get_category_by_id(category_id)

    @pytest.mark.asyncio
    async def test_get_category_by_slug(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        expected = AsyncMock(spec=Category)
        mock_repo.get_category_by_slug.return_value = expected

        result = await service.get_category_by_slug("plumbing")

        mock_repo.get_category_by_slug.assert_called_once_with("plumbing")
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_category_by_slug_not_found(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        mock_repo.get_category_by_slug.return_value = None

        with pytest.raises(CategoryNotFoundError):
            await service.get_category_by_slug("plumbing")

    @pytest.mark.asyncio
    async def test_list_categories(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        expected = [AsyncMock(spec=Category)]
        mock_repo.list_categories.return_value = expected

        result = await service.list_categories()

        mock_repo.list_categories.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def test_update_category(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        category = AsyncMock(spec=Category)
        mock_repo.update_category.return_value = category

        result = await service.update_category(category)

        mock_repo.update_category.assert_called_once_with(category)
        assert result == category

    @pytest.mark.asyncio
    async def test_delete_category(self):
        mock_repo = AsyncMock(spec=CategoryRepository)
        service = CategoryService(category_repository=mock_repo)
        category_id = CategoryId()
        mock_repo.delete_category.return_value = None

        await service.delete_category(category_id)

        mock_repo.delete_category.assert_called_once_with(category_id)

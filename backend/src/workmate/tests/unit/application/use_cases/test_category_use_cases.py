from datetime import datetime, UTC

import pytest
from unittest.mock import AsyncMock

from workmate.application.dtos.category_dtos import CreateCategoryRequest, UpdateCategoryRequest
from workmate.application.use_cases.category_use_cases import CategoryUseCases
from workmate.domain.models.category import Category, CategoryId
from workmate.domain.services.category_service import CategoryService


class TestCategoryUseCases:
    @pytest.fixture
    def mock_category_service(self):
        return AsyncMock(spec=CategoryService)

    @pytest.fixture
    def use_cases(self, mock_category_service):
        return CategoryUseCases(category_service=mock_category_service)

    @pytest.mark.asyncio
    async def test_create_category(self, use_cases, mock_category_service):
        request = CreateCategoryRequest(
            name="Plumbing",
            slug="plumbing",
            icon="wrench",
            description="All plumbing services",
            parent_id=None,
            is_active=True,
            display_order=1,
        )
        created_category = Category(
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
        mock_category_service.create_category.return_value = created_category

        result = await use_cases.create_category(request)

        mock_category_service.create_category.assert_called_once()
        assert result.name == "Plumbing"
        assert result.slug == "plumbing"
        assert result.display_order == 1

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, use_cases, mock_category_service):
        category = Category(
            id=CategoryId(),
            name="Electrical",
            slug="electrical",
            icon=None,
            description=None,
            parent_id=None,
            is_active=True,
            display_order=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_category_service.get_category_by_id.return_value = category

        result = await use_cases.get_category_by_id(str(category.id))

        mock_category_service.get_category_by_id.assert_called_once()
        assert result.id == category.id
        assert result.slug == "electrical"

    @pytest.mark.asyncio
    async def test_get_category_by_slug(self, use_cases, mock_category_service):
        category = Category(
            id=CategoryId(),
            name="Gardening",
            slug="gardening",
            icon=None,
            description=None,
            parent_id=None,
            is_active=True,
            display_order=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_category_service.get_category_by_slug.return_value = category

        result = await use_cases.get_category_by_slug("gardening")

        mock_category_service.get_category_by_slug.assert_called_once_with("gardening")
        assert result.slug == "gardening"

    @pytest.mark.asyncio
    async def test_list_categories(self, use_cases, mock_category_service):
        categories = [
            Category(
                id=CategoryId(),
                name="Cleaning",
                slug="cleaning",
                icon=None,
                description=None,
                parent_id=None,
                is_active=True,
                display_order=0,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]
        mock_category_service.list_categories.return_value = categories

        result = await use_cases.list_categories()

        mock_category_service.list_categories.assert_called_once()
        assert len(result) == 1
        assert result[0].slug == "cleaning"

    @pytest.mark.asyncio
    async def test_update_category(self, use_cases, mock_category_service):
        existing = Category(
            id=CategoryId(),
            name="Carpentry",
            slug="carpentry",
            icon=None,
            description="Old",
            parent_id=None,
            is_active=True,
            display_order=0,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        mock_category_service.get_category_by_id.return_value = existing

        updated_saved = Category(
            id=existing.id,
            name="Home Carpentry",
            slug="home-carpentry",
            icon="hammer",
            description="New",
            parent_id=None,
            is_active=False,
            display_order=2,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
        )
        mock_category_service.update_category.return_value = updated_saved

        request = UpdateCategoryRequest(
            name="Home Carpentry",
            slug="home-carpentry",
            icon="hammer",
            description="New",
            is_active=False,
            display_order=2,
        )

        result = await use_cases.update_category(str(existing.id), request)

        mock_category_service.get_category_by_id.assert_called_once()
        mock_category_service.update_category.assert_called_once()
        updated_arg = mock_category_service.update_category.call_args[0][0]
        assert updated_arg.name == "Home Carpentry"
        assert updated_arg.slug == "home-carpentry"
        assert updated_arg.icon == "hammer"
        assert updated_arg.is_active is False
        assert result.name == "Home Carpentry"

    @pytest.mark.asyncio
    async def test_delete_category(self, use_cases, mock_category_service):
        await use_cases.delete_category(str(CategoryId()))

        mock_category_service.delete_category.assert_called_once()

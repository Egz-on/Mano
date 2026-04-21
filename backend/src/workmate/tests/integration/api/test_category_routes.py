from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from workmate.tests.test_fixtures import create_test_category

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient, auth_header_admin: dict[str, str]):
    payload = {
        "name": "Plumbing",
        "slug": "plumbing",
        "icon": "wrench",
        "description": "All plumbing related services",
        "is_active": True,
        "display_order": 1,
    }
    response = await async_client.post("/api/v1/categories/", json=payload, headers=auth_header_admin)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Plumbing"
    assert data["slug"] == "plumbing"
    assert data["icon"] == "wrench"


@pytest.mark.asyncio
async def test_get_category(async_client: AsyncClient, db_session: "AsyncSession"):
    category = await create_test_category(
        db_session=db_session,
        name_mk="Electrical",
        slug="electrical",
    )
    response = await async_client.get(f"/api/v1/categories/{category['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category["id"]
    assert data["slug"] == "electrical"


@pytest.mark.asyncio
async def test_update_category(
    async_client: AsyncClient, db_session: "AsyncSession", auth_header_admin: dict[str, str]
):
    category = await create_test_category(
        db_session=db_session,
        name_mk="Carpentry",
        slug="carpentry",
    )
    payload = {"name": "Home Carpentry", "slug": "home-carpentry", "display_order": 3}
    response = await async_client.put(f"/api/v1/categories/{category['id']}", json=payload, headers=auth_header_admin)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Home Carpentry"
    assert data["slug"] == "home-carpentry"
    assert data["display_order"] == 3


@pytest.mark.asyncio
async def test_delete_category(
    async_client: AsyncClient, db_session: "AsyncSession", auth_header_admin: dict[str, str]
):
    category = await create_test_category(db_session=db_session, name_mk="Painting", slug="painting")
    response = await async_client.delete(f"/api/v1/categories/{category['id']}", headers=auth_header_admin)
    assert response.status_code == 204

    # Verify deletion
    response = await async_client.get(f"/api/v1/categories/{category['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_categories(async_client: AsyncClient, db_session: "AsyncSession"):
    await create_test_category(db_session=db_session, name_mk="Gardening", slug="gardening")
    await create_test_category(db_session=db_session, name_mk="Cleaning", slug="cleaning")

    response = await async_client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2

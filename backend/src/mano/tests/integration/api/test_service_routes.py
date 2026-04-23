from typing import TYPE_CHECKING, Any

import pytest
from httpx import AsyncClient
from mano.tests.test_fixtures import create_test_provider, create_test_category, create_test_service

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_provider(db_session: "AsyncSession"):
    """Create a test provider using factory function."""
    provider = await create_test_provider(
        db_session=db_session,
        auth_user_id="00000000-0000-0000-0000-000000000001",
        name="Test",
        surname="Provider",
        phone="+38970123456",
    )
    return provider


@pytest.fixture
async def test_category(db_session: "AsyncSession"):
    """Create a test category using factory function."""
    category = await create_test_category(
        db_session=db_session,
        name_mk="Plumbing",
        slug="plumbing",
    )
    return category


@pytest.mark.asyncio
async def test_create_service(
    async_client: AsyncClient,
    test_provider: dict[str, Any],
    test_category: dict[str, Any],
    auth_header_provider: dict[str, str],
):
    payload = {
        "provider_id": test_provider["id"],
        "category_id": test_category["id"],
        "title": "Fix Leaks",
        "description": "Professional leak fixing service with 10 chars",
        "price": 500.0,
        "currency": "MKD",
        "pricing_type": "fixed",
        "service_areas": ["Skopje"],
        "is_active": True,
    }
    response = await async_client.post("/api/v1/services/", json=payload, headers=auth_header_provider)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Fix Leaks"
    assert data["price"] == 500.0
    assert data["provider_id"] == test_provider["id"]


@pytest.mark.asyncio
async def test_get_service(
    async_client: AsyncClient, test_provider: dict[str, Any], test_category: dict[str, Any], db_session: "AsyncSession"
):
    # Create service using factory function
    service = await create_test_service(
        db_session=db_session,
        provider_id=test_provider["id"],
        category_id=test_category["id"],
        title="Test Service",
        description="Description length check",
        price=100.0,
        pricing_type="fixed",
    )
    service_id = service["id"]

    response = await async_client.get(f"/api/v1/services/{service_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == service_id
    assert data["title"] == "Test Service"


@pytest.mark.asyncio
async def test_list_services(
    async_client: AsyncClient, test_provider: dict[str, Any], test_category: dict[str, Any], db_session: "AsyncSession"
):
    # Create service using factory function
    await create_test_service(
        db_session=db_session,
        provider_id=test_provider["id"],
        category_id=test_category["id"],
        title="Service A",
        description="Description length check",
        price=100.0,
        pricing_type="fixed",
    )

    response = await async_client.get("/api/v1/services/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_services_with_location_filter(
    async_client: AsyncClient,
    test_category: dict[str, Any],
    db_session: "AsyncSession",
):
    nearby_provider = await create_test_provider(
        db_session=db_session,
        auth_user_id="00000000-0000-0000-0000-000000000011",
        name="Near",
        surname="Provider",
        phone="+38970123457",
        company_name="Near Services",
        location="POINT (21.4254 41.9981)",
    )
    far_provider = await create_test_provider(
        db_session=db_session,
        auth_user_id="00000000-0000-0000-0000-000000000012",
        name="Far",
        surname="Provider",
        phone="+38970123458",
        company_name="Far Services",
        location="POINT (20.4489 44.7866)",
    )

    await create_test_service(
        db_session=db_session,
        provider_id=nearby_provider["id"],
        category_id=test_category["id"],
        title="Nearby Plumbing",
        description="Nearby service description",
        price=100.0,
        pricing_type="fixed",
    )
    await create_test_service(
        db_session=db_session,
        provider_id=far_provider["id"],
        category_id=test_category["id"],
        title="Far Plumbing",
        description="Far away service description",
        price=120.0,
        pricing_type="fixed",
    )

    response = await async_client.get("/api/v1/services/?latitude=41.9981&longitude=21.4254&radius_km=10")
    assert response.status_code == 200
    data = response.json()
    titles = [item["title"] for item in data["items"]]
    assert "Nearby Plumbing" in titles
    assert "Far Plumbing" not in titles

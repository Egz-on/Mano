from typing import TYPE_CHECKING, Any

import pytest
from httpx import AsyncClient

from mano.tests.test_fixtures import create_test_provider, create_test_availability

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_provider(db_session: "AsyncSession"):
    """Create a test provider using factory function."""
    return await create_test_provider(
        db_session=db_session,
        auth_user_id="00000000-0000-0000-0000-000000000001",
        name="Test",
        surname="Provider",
        phone="+38970123456",
    )


@pytest.mark.asyncio
async def test_create_availability(
    async_client: AsyncClient, test_provider: dict[str, Any], auth_header_provider: dict[str, str]
):
    payload = {
        "provider_id": test_provider["id"],
        "day_of_week": 1,
        "start_time": "09:00",
        "end_time": "17:00",
        "is_available": True,
    }
    response = await async_client.post("/api/v1/availability/", json=payload, headers=auth_header_provider)
    assert response.status_code == 201
    data = response.json()
    assert data["provider_id"] == test_provider["id"]
    assert data["day_of_week"] == 1
    assert data["start_time"] == "09:00"


@pytest.mark.asyncio
async def test_get_availability(async_client: AsyncClient, test_provider: dict[str, Any], db_session: "AsyncSession"):
    availability = await create_test_availability(db_session=db_session, provider_id=test_provider["id"])

    response = await async_client.get(f"/api/v1/availability/{availability['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == availability["id"]
    assert data["provider_id"] == test_provider["id"]


@pytest.mark.asyncio
async def test_update_availability(
    async_client: AsyncClient,
    test_provider: dict[str, Any],
    db_session: "AsyncSession",
    auth_header_provider: dict[str, str],
):
    availability = await create_test_availability(
        db_session=db_session,
        provider_id=test_provider["id"],
        day_of_week=2,
        start_time="08:00",
        end_time="12:00",
    )
    payload = {"start_time": "10:00", "end_time": "14:00", "is_available": False}
    response = await async_client.put(
        f"/api/v1/availability/{availability['id']}",
        json=payload,
        headers=auth_header_provider,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["start_time"] == "10:00"
    assert data["end_time"] == "14:00"
    assert data["is_available"] is False


@pytest.mark.asyncio
async def test_delete_availability(
    async_client: AsyncClient,
    test_provider: dict[str, Any],
    db_session: "AsyncSession",
    auth_header_provider: dict[str, str],
):
    availability = await create_test_availability(db_session=db_session, provider_id=test_provider["id"])

    response = await async_client.delete(
        f"/api/v1/availability/{availability['id']}",
        headers=auth_header_provider,
    )
    assert response.status_code == 204

    response = await async_client.get(f"/api/v1/availability/{availability['id']}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_availability(async_client: AsyncClient, test_provider: dict[str, Any], db_session: "AsyncSession"):
    await create_test_availability(db_session=db_session, provider_id=test_provider["id"])
    await create_test_availability(db_session=db_session, provider_id=test_provider["id"], day_of_week=3)

    response = await async_client.get("/api/v1/availability/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2

    response = await async_client.get(f"/api/v1/availability/?provider_id={test_provider['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 2

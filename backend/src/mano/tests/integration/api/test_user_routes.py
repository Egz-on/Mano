from typing import TYPE_CHECKING, Any
from uuid import NAMESPACE_DNS, uuid5

import pytest
from httpx import AsyncClient
from mano.tests.test_fixtures import create_test_user

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_user(db_session: "AsyncSession"):
    """Create a test user using factory function."""
    auth_user_id = str(uuid5(NAMESPACE_DNS, "mano:client@mano.com"))
    user = await create_test_user(
        db_session=db_session,
        auth_user_id=auth_user_id,
        name="Test",
        surname="User",
        phone="+38970123456",
        role="client",
    )
    return user


@pytest.mark.asyncio
async def test_get_my_profile(async_client: AsyncClient, test_user: dict[str, Any], auth_header_client: dict[str, str]):
    response = await async_client.get("/api/v1/users/me", headers=auth_header_client)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user["id"]
    assert data["name"] == "Test"
    assert data["surname"] == "User"


@pytest.mark.asyncio
async def test_update_my_profile(
    async_client: AsyncClient, test_user: dict[str, Any], auth_header_client: dict[str, str]
):
    payload = {
        "name": "Updated",
        "surname": "Name",
        "city": "Skopje",
        "latitude": 41.9981,
        "longitude": 21.4254,
        "fcm_token": "test-device-token",
    }
    response = await async_client.put("/api/v1/users/me", json=payload, headers=auth_header_client)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["surname"] == "Name"
    assert data["city"] == "Skopje"
    assert data["latitude"] == 41.9981
    assert data["longitude"] == 21.4254
    assert data["fcm_token"] == "test-device-token"


@pytest.mark.asyncio
async def test_access_without_token(async_client: AsyncClient):
    response = await async_client.get("/api/v1/users/me")
    assert response.status_code == 401

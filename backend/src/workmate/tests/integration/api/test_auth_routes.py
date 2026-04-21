from __future__ import annotations

import pytest
from httpx import AsyncClient

from workmate.infrastructure.config.settings import get_settings


@pytest.mark.asyncio
async def test_register_and_login_flow(async_client: AsyncClient) -> None:
    register_payload = {
        "email": "new.user@workmate.com",
        "password": "StrongPass123",
        "full_name": "New User",
        "phone": "+38970123456",
        "role": "client",
    }

    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    register_data = register_response.json()
    assert register_data["user"]["email"] == "new.user@workmate.com"
    assert register_data["user"]["full_name"] == "New User"
    assert register_data["user"]["role"] == "client"
    assert register_data["access_token"]

    me_response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {register_data['access_token']}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "new.user@workmate.com"
    assert me_data["full_name"] == "New User"

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "new.user@workmate.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_demo_login_still_works(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@workmate.com", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(async_client: AsyncClient) -> None:
    register_payload = {
        "email": "reset.user@workmate.com",
        "password": "InitialPass123",
        "full_name": "Reset User",
        "phone": "+38970987654",
    }
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    forgot_response = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset.user@workmate.com"},
    )
    assert forgot_response.status_code == 200

    forgot_data = forgot_response.json()
    assert "message" in forgot_data
    if get_settings().is_development:
        assert forgot_data["reset_token"] is not None
    else:
        assert forgot_data["reset_token"] is None

    reset_response = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": forgot_data["reset_token"] or "missing-token", "new_password": "UpdatedPass123"},
    )
    assert reset_response.status_code == 200 if forgot_data["reset_token"] else 400

    if forgot_data["reset_token"]:
        old_login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "reset.user@workmate.com", "password": "InitialPass123"},
        )
        assert old_login_response.status_code == 401

        new_login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "reset.user@workmate.com", "password": "UpdatedPass123"},
        )
        assert new_login_response.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_does_not_leak(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing.user@workmate.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["reset_token"] is None

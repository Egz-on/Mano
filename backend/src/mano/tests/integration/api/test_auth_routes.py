from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_flow(async_client: AsyncClient) -> None:
    register_payload = {
        "email": "new.user@mano.com",
        "password": "StrongPass123",
        "name": "New",
        "surname": "User",
        "phone": "+393470123456",
        "role": "client",
    }

    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    register_data = register_response.json()
    assert register_data["user"]["email"] == "new.user@mano.com"
    assert register_data["user"]["name"] == "New"
    assert register_data["user"]["surname"] == "User"
    assert register_data["user"]["role"] == "client"
    assert register_data["access_token"]

    me_response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {register_data['access_token']}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "new.user@mano.com"
    assert me_data["name"] == "New"
    assert me_data["surname"] == "User"

    login_response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "new.user@mano.com", "password": "StrongPass123"},
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_demo_login_still_works(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@mano.com", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(async_client: AsyncClient) -> None:
    register_payload = {
        "email": "reset.user@mano.com",
        "password": "InitialPass123",
        "name": "Reset",
        "surname": "User",
        "phone": "+393470987654",
    }
    register_response = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201

    forgot_response = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "reset.user@mano.com"},
    )
    assert forgot_response.status_code == 200

    forgot_data = forgot_response.json()
    assert "message" in forgot_data
    assert "reset_token" in forgot_data

    reset_response = await async_client.post(
        "/api/v1/auth/reset-password",
        json={"token": forgot_data["reset_token"] or "missing-token", "new_password": "UpdatedPass123"},
    )
    assert reset_response.status_code == 200 if forgot_data["reset_token"] else 400

    if forgot_data["reset_token"]:
        old_login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "reset.user@mano.com", "password": "InitialPass123"},
        )
        assert old_login_response.status_code == 401

        new_login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "reset.user@mano.com", "password": "UpdatedPass123"},
        )
        assert new_login_response.status_code == 200


@pytest.mark.asyncio
async def test_forgot_password_unknown_email_does_not_leak(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "missing.user@mano.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["reset_token"] is None

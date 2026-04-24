from uuid import NAMESPACE_DNS, uuid5

import pytest
from httpx import AsyncClient

from mano.tests.test_fixtures import create_test_category, create_test_provider, create_test_user


@pytest.fixture
async def test_client_user(db_session):
    return await create_test_user(
        db_session=db_session,
        auth_user_id=str(uuid5(NAMESPACE_DNS, "mano:client@mano.com")),
        name="Job",
        surname="Client",
        phone="+393470123459",
        role="client",
    )


@pytest.fixture
async def test_provider_user(db_session):
    return await create_test_provider(
        db_session=db_session,
        auth_user_id="00000000-0000-0000-0000-000000000001",
        name="Job",
        surname="Technician",
        phone="+393470123456",
    )


@pytest.fixture
async def test_job_category(db_session):
    return await create_test_category(db_session=db_session, name_mk="Electrical", slug="electrical")


@pytest.mark.asyncio
async def test_client_can_create_and_list_jobs(
    async_client: AsyncClient,
    test_client_user,
    test_job_category,
    auth_header_client,
):
    payload = {
        "customer_id": test_client_user["id"],
        "category_id": test_job_category["id"],
        "description": "Power outlet is sparking in the kitchen",
        "latitude": 41.9981,
        "longitude": 21.4254,
        "address": "Client Street 1",
        "photo_urls": ["https://example.com/outlet.jpg"],
    }

    create_response = await async_client.post("/api/v1/jobs/", json=payload, headers=auth_header_client)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "pending"
    assert created["customer_id"] == test_client_user["id"]

    list_response = await async_client.get("/api/v1/jobs/", headers=auth_header_client)
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_quote_flow_from_assignment_to_approval(
    async_client: AsyncClient,
    test_client_user,
    test_provider_user,
    test_job_category,
    auth_header_client,
    auth_header_provider,
):
    create_response = await async_client.post(
        "/api/v1/jobs/",
        json={
            "customer_id": test_client_user["id"],
            "category_id": test_job_category["id"],
            "description": "Circuit breaker keeps tripping all evening",
            "latitude": 41.9981,
            "longitude": 21.4254,
            "address": "Client Street 2",
        },
        headers=auth_header_client,
    )
    job_id = create_response.json()["id"]

    assign_response = await async_client.post(
        f"/api/v1/jobs/{job_id}/assign",
        json={"technician_id": test_provider_user["id"]},
        headers=auth_header_client,
    )
    assert assign_response.status_code == 200
    assert assign_response.json()["status"] == "assigned"

    quote_response = await async_client.post(
        f"/api/v1/jobs/{job_id}/quote",
        json={"amount": "250.00", "description": "Breaker replacement and diagnostics"},
        headers=auth_header_provider,
    )
    assert quote_response.status_code == 200
    assert quote_response.json()["status"] == "diagnosed"

    approve_response = await async_client.post(
        f"/api/v1/jobs/{job_id}/quote/approve",
        headers=auth_header_client,
    )
    assert approve_response.status_code == 200
    approved = approve_response.json()
    assert approved["status"] == "quote_approved"
    assert approved["chat_unlocked"] is True
    assert approved["call_out_fee_paid"] is True

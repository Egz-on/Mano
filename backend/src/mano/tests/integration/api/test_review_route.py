from typing import TYPE_CHECKING, Any
import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, UTC
from mano.tests.test_fixtures import (
    create_test_provider,
    create_test_category,
    create_test_service,
    create_test_user,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def test_reviewer(db_session: "AsyncSession"):
    return await create_test_user(db_session, auth_user_id=str(uuid4()), full_name="Reviewer Bob")


@pytest.fixture
async def test_provider(db_session: "AsyncSession"):
    return await create_test_provider(db_session, auth_user_id=str(uuid4()))


@pytest.fixture
async def test_category(db_session: "AsyncSession"):
    return await create_test_category(db_session)


@pytest.mark.asyncio
async def test_review_crud_flow(
    async_client: AsyncClient,
    test_provider: dict[str, Any],
    test_category: dict[str, Any],
    test_reviewer: dict[str, Any],
    db_session: "AsyncSession",
):
    # Setup service
    service = await create_test_service(db_session, test_provider["id"], test_category["id"])
    service_id = service["id"]

    # 1. Create Review
    # Note: ReviewCreateSchema currently requires many fields that should ideally be inferred,
    # but we must match the schema.
    payload = {
        "user_id": test_reviewer["id"],
        "client_id": test_reviewer["id"],
        "provider_id": test_provider["id"],
        "service_id": service_id,
        "rating": 5,
        "comment": "Nice!",
        "status": "pending",
        "moderated_by": str(uuid4()),  # Valid UUID logic required
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
        # moderation_notes is optional
    }

    response = await async_client.post("/api/v1/reviews/", json=payload)
    assert response.status_code == 201, f"Failed to create review: {response.text}"
    data = response.json()
    review_id = data["id"]
    assert data["comment"] == "Nice!"

    # 2. Get Review
    response = await async_client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 200
    assert response.json()["id"] == review_id

    # 3. List Reviews for Service
    response = await async_client.get(f"/api/v1/reviews/?service_id={service_id}")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    found = False
    for item in items:
        if item["id"] == review_id:
            found = True
            break
    assert found

    # 4. Update Review
    update_payload = {"rating": 3, "comment": "Changed my mind"}
    response = await async_client.put(f"/api/v1/reviews/{review_id}", json=update_payload)
    assert response.status_code == 200, f"Update failed: {response.text}"
    assert response.json()["rating"] == 3
    assert response.json()["comment"] == "Changed my mind"

    # 5. Delete Review
    response = await async_client.delete(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 204

    # Verify deletion
    response = await async_client.get(f"/api/v1/reviews/{review_id}")
    assert response.status_code == 404

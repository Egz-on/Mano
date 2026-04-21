import pytest
from mano.domain.models.service_model import Service, ServiceId, ProviderId, CategoryId
import uuid


def test_service_id_creation():
    sid = ServiceId()
    assert uuid.UUID(sid.value)


def test_service_update_description_success():
    service = Service(
        id=ServiceId(),
        provider_id=ProviderId(),
        category_id=CategoryId(),
        title="Valid Service",
        description="Original description",
        price=10.0,
    )
    new_desc = "Updated description that is long enough"
    updated = service.update_description(new_desc)
    assert updated.description == new_desc
    assert updated is not service


def test_service_update_description_too_short():
    service = Service(
        id=ServiceId(),
        provider_id=ProviderId(),
        category_id=CategoryId(),
        title="Valid Service",
        description="Original description",
        price=10.0,
    )
    with pytest.raises(ValueError, match="Description must be at least 10 characters long"):
        service.update_description("short")


def test_service_activation_deactivation():
    service = Service(
        id=ServiceId(),
        provider_id=ProviderId(),
        category_id=CategoryId(),
        title="Valid Service",
        description="Valid description",
        price=10.0,
        is_active=True,
    )
    deactivated = service.deactive()
    assert deactivated.is_active is False

    activated = deactivated.active()
    assert activated.is_active is True


def test_service_to_dict():
    service = Service(
        id=ServiceId("e407f3f4-3075-4089-a29d-fb2c42d992a0"),
        provider_id=ProviderId("e407f3f4-3075-4089-a29d-fb2c42d992a1"),
        category_id=CategoryId("e407f3f4-3075-4089-a29d-fb2c42d992a2"),
        title="Test Title",
        description="Test Description",
        price=100.0,
    )
    d = service.to_dict()
    assert d["id"] == "e407f3f4-3075-4089-a29d-fb2c42d992a0"
    assert d["title"] == "Test Title"
    assert d["price"] == 100.0

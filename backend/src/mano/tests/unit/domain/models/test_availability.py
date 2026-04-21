from datetime import datetime, UTC

from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId


class TestAvailability:
    def test_update_availability(self):
        availability = Availability(
            id=AvailabilityId(),
            provider_id=ProviderId(),
            day_of_week=1,
            start_time="09:00",
            end_time="17:00",
            is_available=True,
            specific_date=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        updated = availability.update(start_time="10:00", end_time="18:00", is_available=False)

        assert updated.start_time == "10:00"
        assert updated.end_time == "18:00"
        assert updated.is_available is False

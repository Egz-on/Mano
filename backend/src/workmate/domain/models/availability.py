"""Availability domain model."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
import uuid

from workmate.domain.models.service_model import ProviderId


@dataclass(frozen=True)
class AvailabilityId:
    """Availability identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Availability:
    """Availability domain entity."""

    id: AvailabilityId
    provider_id: ProviderId
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool
    specific_date: datetime | None
    created_at: datetime
    updated_at: datetime

    def update(
        self,
        day_of_week: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        is_available: bool | None = None,
        specific_date: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "Availability":
        """Update availability details."""
        return replace(
            self,
            day_of_week=day_of_week if day_of_week is not None else self.day_of_week,
            start_time=start_time if start_time is not None else self.start_time,
            end_time=end_time if end_time is not None else self.end_time,
            is_available=is_available if is_available is not None else self.is_available,
            specific_date=specific_date if specific_date is not None else self.specific_date,
            updated_at=updated_at if updated_at is not None else datetime.now(),
        )

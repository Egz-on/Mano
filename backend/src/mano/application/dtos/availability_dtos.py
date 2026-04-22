"""Availability DTOs for application layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId


@dataclass(frozen=True)
class CreateAvailabilityRequest:
    """DTO for creating availability."""

    provider_id: ProviderId
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool = True
    specific_date: datetime | None = None


@dataclass(frozen=True)
class UpdateAvailabilityRequest:
    """DTO for updating availability."""

    day_of_week: int | None = None
    start_time: str | None = None
    end_time: str | None = None
    is_available: bool | None = None
    specific_date: datetime | None = None


@dataclass(frozen=True)
class AvailabilityResponseDTO:
    """DTO for availability response."""

    id: AvailabilityId
    provider_id: ProviderId
    day_of_week: int
    start_time: str
    end_time: str
    is_available: bool
    specific_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_domain(cls, availability: Availability) -> AvailabilityResponseDTO:
        """Convert domain Availability to AvailabilityResponseDTO."""
        return cls(
            id=availability.id,
            provider_id=availability.provider_id,
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_available=availability.is_available,
            specific_date=availability.specific_date,
            created_at=availability.created_at,
            updated_at=availability.updated_at,
        )

"""Availability domain service implementation."""

from __future__ import annotations

from workmate.domain.models.availability import Availability, AvailabilityId
from workmate.domain.models.service_model import ProviderId
from workmate.domain.repositories.availability_repository import AvailabilityRepository
from workmate.domain.exceptions.base import DomainError


class AvailabilityService:
    """Availability domain service for business logic operations."""

    def __init__(self, availability_repository: AvailabilityRepository):
        """Initialize availability service."""
        self.availability_repository = availability_repository

    async def create_availability(self, availability: Availability) -> Availability:
        """Create a new availability slot."""
        if availability.start_time >= availability.end_time:
            raise DomainError("start_time must be before end_time")
        if availability.day_of_week < 0 or availability.day_of_week > 6:
            raise DomainError("day_of_week must be between 0 and 6")
        return await self.availability_repository.create_availability(availability)

    async def get_availability_by_id(self, availability_id: AvailabilityId) -> Availability | None:
        """Get availability by ID."""
        return await self.availability_repository.get_availability_by_id(availability_id)

    async def list_by_provider(self, provider_id: ProviderId) -> list[Availability]:
        """List availability slots for a provider."""
        return await self.availability_repository.list_by_provider(provider_id)

    async def list_all(self) -> list[Availability]:
        """List all availability slots."""
        return await self.availability_repository.list_all()

    async def update_availability(self, availability: Availability) -> Availability:
        """Update an availability slot."""
        if availability.start_time >= availability.end_time:
            raise DomainError("start_time must be before end_time")
        if availability.day_of_week < 0 or availability.day_of_week > 6:
            raise DomainError("day_of_week must be between 0 and 6")
        return await self.availability_repository.update_availability(availability)

    async def delete_availability(self, availability_id: AvailabilityId) -> None:
        """Delete an availability slot."""
        await self.availability_repository.delete_availability(availability_id)

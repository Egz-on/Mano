"""Availability use cases."""

from __future__ import annotations

from datetime import datetime, UTC

from mano.application.dtos.availability_dtos import (
    AvailabilityResponseDTO,
    CreateAvailabilityRequest,
    UpdateAvailabilityRequest,
)
from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId
from mano.domain.services.availability_service import AvailabilityService
from mano.domain.exceptions.base import AvailabilityNotFoundError


class AvailabilityUseCases:
    """Availability use cases."""

    def __init__(self, availability_service: AvailabilityService) -> None:
        """Initialize availability use cases."""
        self.availability_service = availability_service

    async def create_availability(self, request: CreateAvailabilityRequest) -> AvailabilityResponseDTO:
        """Create a new availability slot."""
        availability = Availability(
            id=AvailabilityId(),
            provider_id=request.provider_id,
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            is_available=request.is_available,
            specific_date=request.specific_date,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        created = await self.availability_service.create_availability(availability)
        return AvailabilityResponseDTO.from_domain(created)

    async def get_availability_by_id(self, availability_id: str) -> AvailabilityResponseDTO:
        """Get availability by ID."""
        availability = await self.availability_service.get_availability_by_id(AvailabilityId(availability_id))
        if not availability:
            raise AvailabilityNotFoundError(f"Availability {availability_id} not found")
        return AvailabilityResponseDTO.from_domain(availability)

    async def list_by_provider(self, provider_id: str) -> list[AvailabilityResponseDTO]:
        """List availability for a provider."""
        slots = await self.availability_service.list_by_provider(ProviderId(provider_id))
        return [AvailabilityResponseDTO.from_domain(s) for s in slots]

    async def list_all(self) -> list[AvailabilityResponseDTO]:
        """List all availability slots."""
        slots = await self.availability_service.list_all()
        return [AvailabilityResponseDTO.from_domain(s) for s in slots]

    async def update_availability(
        self, availability_id: str, request: UpdateAvailabilityRequest
    ) -> AvailabilityResponseDTO:
        """Update an availability slot."""
        availability = await self.availability_service.get_availability_by_id(AvailabilityId(availability_id))
        if not availability:
            raise AvailabilityNotFoundError(f"Availability {availability_id} not found")
        updated = availability.update(
            day_of_week=request.day_of_week,
            start_time=request.start_time,
            end_time=request.end_time,
            is_available=request.is_available,
            specific_date=request.specific_date,
            updated_at=datetime.now(UTC),
        )
        saved = await self.availability_service.update_availability(updated)
        return AvailabilityResponseDTO.from_domain(saved)

    async def delete_availability(self, availability_id: str) -> None:
        """Delete an availability slot."""
        availability = await self.availability_service.get_availability_by_id(AvailabilityId(availability_id))
        if not availability:
            raise AvailabilityNotFoundError(f"Availability {availability_id} not found")
        await self.availability_service.delete_availability(AvailabilityId(availability_id))

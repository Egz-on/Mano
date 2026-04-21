from __future__ import annotations

from abc import ABC, abstractmethod
from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId


class AvailabilityRepository(ABC):
    """Abstract base class for Availability repository."""

    @abstractmethod
    async def create_availability(self, availability: Availability) -> Availability:
        """Create a new availability slot."""
        ...

    @abstractmethod
    async def get_availability_by_id(self, availability_id: AvailabilityId) -> Availability | None:
        """Get availability by ID."""
        ...

    @abstractmethod
    async def list_by_provider(self, provider_id: ProviderId) -> list[Availability]:
        """List availability slots for a provider."""
        ...

    @abstractmethod
    async def list_all(self) -> list[Availability]:
        """List all availability slots."""
        ...

    @abstractmethod
    async def update_availability(self, availability: Availability) -> Availability:
        """Update an availability slot."""
        ...

    @abstractmethod
    async def delete_availability(self, availability_id: AvailabilityId) -> None:
        """Delete an availability slot."""
        ...

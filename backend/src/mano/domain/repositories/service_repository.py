"""User domain service implementation."""

from __future__ import annotations
from abc import ABC, abstractmethod
from ..models.service_model import Service, ServiceId


class ServiceRepository(ABC):
    """Abstract base class for Service repository."""

    @abstractmethod
    async def create_service(self, service: Service) -> Service:
        """Create a new service."""
        ...

    @abstractmethod
    async def get_service_by_id(self, service_id: ServiceId) -> Service | None:
        """Get service by ID."""
        ...

    @abstractmethod
    async def update_service(self, service: Service) -> Service:
        """Update an existing service."""
        ...

    @abstractmethod
    async def delete_service(self, service_id: ServiceId) -> None:
        """Delete a service."""
        ...

    @abstractmethod
    async def list_services(self) -> list[Service]:
        """List all services."""
        ...

    @abstractmethod
    async def get_service_by_title(self, title: str) -> Service | None:
        """Get service by title."""
        ...

    @abstractmethod
    async def list_services_nearby(self, *, latitude: float, longitude: float, radius_km: float) -> list[Service]:
        """List services whose providers are within the given radius."""
        ...

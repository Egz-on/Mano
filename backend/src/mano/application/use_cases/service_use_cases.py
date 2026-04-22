"""Service use cases module."""

from __future__ import annotations
from mano.domain.services.service_services import ServiceService
from mano.domain.models.service_model import Service, ServiceId
from mano.application.dtos.service_dtos import CreateServiceRequest, UpdateServiceRequest, ServiceResponseDTO


class ServiceUseCases:
    """Service use cases class.

    Use Case responsibility:
    1. Convert DTO → Domain (if needed)
    2. Call domain service (business logic)
    3. Convert Domain → DTO
    """

    def __init__(self, service_services: ServiceService):
        """Initialize use cases with domain service dependency."""
        self._service_service = service_services

    async def create_service(self, request: CreateServiceRequest) -> Service:
        """
        Create a new service.

        Use Case responsibility:
        1. Call domain service (business logic validation happens there)
        2. Return domain entity (let caller convert to DTO if needed)
        """
        service = Service.create(
            provider_id=request.provider_id,
            category_id=request.category_id,
            title=request.title,
            description=request.description,
            price=request.price,
            currency=request.currency,
            pricing_type=request.pricing_type,
            service_areas=request.service_areas,
            service_metadata=request.service_metadata,
            images=request.images,
            is_active=request.is_active,
            is_featured=request.is_featured,
        )
        return await self._service_service.create_service(service)

    async def get_service_by_id(self, service_id: ServiceId) -> Service:
        """Get service by ID."""
        return await self._service_service.get_service_by_id(service_id)

    async def update_service(self, service_id: str, request: UpdateServiceRequest) -> Service:
        """Update an existing service."""
        # Get existing service (raises ServiceNotFoundError if not found)
        service = await self._service_service.get_service_by_id(ServiceId(service_id))

        # Update domain entity using its business methods
        updated_service = service.update(
            title=request.title,
            description=request.description,
            price=request.price,
            currency=request.currency,
            pricing_type=request.pricing_type,
            service_areas=request.service_areas,
            service_metadata=request.service_metadata,
            images=request.images,
            is_active=request.is_active,
            is_featured=request.is_featured,
        )

        # Persist through domain service
        return await self._service_service.update_service(updated_service)

    async def delete_service(self, service_id: ServiceId) -> None:
        """Delete a service by ID."""
        await self._service_service.delete_service(service_id)

    async def list_services(self) -> list[ServiceResponseDTO]:
        """List all services."""
        services = await self._service_service.list_services()
        return [ServiceResponseDTO.from_domain(s) for s in services]

    async def list_services_nearby(self, *, latitude: float, longitude: float, radius_km: float) -> list[ServiceResponseDTO]:
        """List services whose providers are within a search radius."""
        services = await self._service_service.list_services_nearby(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )
        return [ServiceResponseDTO.from_domain(s) for s in services]

    async def get_service_by_title(self, title: str) -> ServiceResponseDTO | None:
        """Get service by title."""
        service = await self._service_service.get_service_by_title(title)
        return ServiceResponseDTO.from_domain(service) if service else None

"""Service domain service implementation."""

from __future__ import annotations

from uuid import UUID

from mano.domain.exceptions.base import ServiceAlreadyExistsError, ServiceNotFoundError
from mano.domain.models.service_model import ServiceImage
from ..repositories.image_storage_port import IImageStoragePort
from ..models.service_model import Service, ServiceId
from ..repositories.service_repository import ServiceRepository


class ServiceService:
    """Service domain service for business logic operations."""

    def __init__(self, service_repository: ServiceRepository, image_storage: IImageStoragePort) -> None:
        """Initialize service with repository and image storage dependencies."""
        self.service_repository = service_repository
        self._image_storage = image_storage

    async def upload_service_images(self, service_id: UUID, file_paths: list[str]) -> list[ServiceImage]:
        """Upload images for a service"""
        folder = f"services/{service_id}"
        return await self._image_storage.upload_multiple_images(file_paths, folder)

    async def delete_service_images(self, public_ids: list[str]) -> bool:
        """Delete images for a service."""
        return await self._image_storage.delete_multiple_images(public_ids)

    def get_image_variants(self, public_id: str) -> dict[str, str]:
        """Get different size variants of an image"""
        return {
            "original": self._image_storage.get_optimized_url(public_id),
            "large": self._image_storage.get_optimized_url(public_id, width=1200),
            "medium": self._image_storage.get_optimized_url(public_id, width=800),
            "small": self._image_storage.get_optimized_url(public_id, width=400),
            "thumbnail": self._image_storage.get_optimized_url(public_id, width=300, height=300),
        }

    async def create_service(self, service: Service) -> Service:
        """
        Create a new service with business logic validation.

        Service responsibility:
        1. Business rules validation
        2. Domain logic
        3. Coordinate with repository
        """
        # Business rule: Service title must be unique (no duplicate titles)
        existing_service = await self.service_repository.get_service_by_title(service.title)
        if existing_service:
            raise ServiceAlreadyExistsError(f"Service with title '{service.title}' already exists")

        # Persist the service
        return await self.service_repository.create_service(service)

    async def get_service_by_id(self, service_id: ServiceId) -> Service:
        """Get service by ID with business logic."""
        service = await self.service_repository.get_service_by_id(service_id)
        if not service:
            raise ServiceNotFoundError(f"Service {service_id} not found")
        return service

    async def update_service(self, service: Service) -> Service:
        """Update an existing service with business logic."""
        return await self.service_repository.update_service(service)

    async def delete_service(self, service_id: ServiceId) -> None:
        """Delete a service with business logic."""
        await self.service_repository.delete_service(service_id)

    async def list_services(self) -> list[Service]:
        """List all services with business logic."""
        return await self.service_repository.list_services()

    async def get_service_by_title(self, title: str) -> Service | None:
        """Get service by title with business logic."""
        return await self.service_repository.get_service_by_title(title)

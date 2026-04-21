"""SQLAlchemy implementation of ServiceRepository for DDD architecture."""

from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from mano.domain.models.service_model import CategoryId, ProviderId, Service, ServiceId
from mano.domain.repositories.service_repository import ServiceRepository
from mano.infrastructure.database.models import ServiceModel
from mano.common.uuid_utils import uuid_to_str


class SQLAlchemyServiceRepository(ServiceRepository):
    """SQLAlchemy implementation of the ServiceRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    # =====================
    # Mapping helpers
    # =====================

    @staticmethod
    def _to_domain(model: ServiceModel) -> Service:
        """Convert database model to domain entity."""
        return Service(
            id=ServiceId(str(model.id)),
            provider_id=ProviderId(str(model.provider_id)),
            category_id=CategoryId(str(model.category_id)),
            title=model.title,
            description=model.description,
            price=model.price,
            currency=model.currency or "MKD",
            pricing_type=model.pricing_type or "fixed",
            service_areas=model.service_areas or [],
            service_metadata=model.service_metadata or {},
            images=model.images or [],
            is_active=model.is_active,
            is_featured=model.is_featured,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _apply_domain_to_model(domain: Service, model: ServiceModel) -> None:
        """Apply domain model changes to database model."""
        model.provider_id = uuid_to_str(domain.provider_id)
        model.category_id = uuid_to_str(domain.category_id)
        model.title = domain.title
        model.description = domain.description
        model.price = domain.price
        model.currency = domain.currency
        model.pricing_type = domain.pricing_type
        model.service_areas = domain.service_areas or []
        model.service_metadata = domain.service_metadata or {}
        model.images = domain.images or []
        model.is_active = domain.is_active
        model.is_featured = domain.is_featured
        model.updated_at = domain.updated_at

    # =====================
    # Repository methods
    # =====================

    async def create_service(self, service: Service) -> Service:
        """Create a new service."""
        model = ServiceModel(
            id=uuid_to_str(service.id),
            provider_id=uuid_to_str(service.provider_id),
            category_id=uuid_to_str(service.category_id),
            title=service.title,
            description=service.description,
            price=service.price,
            currency=service.currency,
            pricing_type=service.pricing_type,
            service_areas=service.service_areas or [],
            service_metadata=service.service_metadata or {},
            images=service.images or [],
            is_active=service.is_active,
            is_featured=service.is_featured,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )
        self._session.add(model)
        await self._session.flush()  # Ensure the model gets persisted
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_service_by_id(self, service_id: ServiceId) -> Service | None:
        """Get service by ID."""
        stmt = select(ServiceModel).where(ServiceModel.id == uuid_to_str(service_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_service(self, service: Service) -> Service:
        """Update an existing service."""
        stmt = select(ServiceModel).where(ServiceModel.id == uuid_to_str(service.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Service with ID {service.id} not found.")

        self._apply_domain_to_model(service, model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete_service(self, service_id: ServiceId) -> None:
        """Delete a service by ID."""
        stmt = delete(ServiceModel).where(ServiceModel.id == uuid_to_str(service_id))
        await self._session.execute(stmt)
        # No need to flush, let the calling code commit

    async def list_services(self) -> list[Service]:
        """List all services."""
        stmt = select(ServiceModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_service_by_title(self, title: str) -> Service | None:
        """Get service by title."""
        stmt = select(ServiceModel).where(ServiceModel.title == title)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

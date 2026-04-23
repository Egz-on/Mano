"""SQLAlchemy implementation of ServiceRepository for DDD architecture."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from geoalchemy2 import Geography
from shapely import wkt
from sqlalchemy import cast, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from mano.domain.exceptions.base import ServiceNotFoundError
from mano.domain.models.service_model import CategoryId, ProviderId, Service, ServiceId
from mano.domain.repositories.service_repository import ServiceRepository
from mano.infrastructure.database.models import ServiceModel, UserProfileModel
from mano.common.uuid_utils import uuid_to_str


class SQLAlchemyServiceRepository(ServiceRepository):
    """SQLAlchemy implementation of the ServiceRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    @staticmethod
    def _distance_km(*, latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
        earth_radius_km = 6371.0
        delta_lat = radians(latitude_b - latitude_a)
        delta_lon = radians(longitude_b - longitude_a)
        latitude_a_rad = radians(latitude_a)
        latitude_b_rad = radians(latitude_b)

        haversine = sin(delta_lat / 2) ** 2 + cos(latitude_a_rad) * cos(latitude_b_rad) * sin(delta_lon / 2) ** 2
        return 2 * earth_radius_km * asin(sqrt(haversine))

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
            raise ServiceNotFoundError(f"Service with ID {service.id} not found.")

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

    async def list_services_nearby(self, *, latitude: float, longitude: float, radius_km: float) -> list[Service]:
        """List services whose providers are within a search radius."""
        bind = self._session.bind
        if bind is None or bind.dialect.name != "postgresql":
            stmt = (
                select(ServiceModel, UserProfileModel.location)
                .join(UserProfileModel, ServiceModel.provider_id == UserProfileModel.id)
                .where(ServiceModel.is_active.is_(True))
                .where(UserProfileModel.location.is_not(None))
            )
            result = await self._session.execute(stmt)
            matches: list[tuple[float, Service]] = []
            for service_model, raw_location in result.all():
                point = wkt.loads(raw_location)
                distance_km = self._distance_km(
                    latitude_a=latitude,
                    longitude_a=longitude,
                    latitude_b=float(point.y),
                    longitude_b=float(point.x),
                )
                if distance_km <= radius_km:
                    matches.append((distance_km, self._to_domain(service_model)))
            matches.sort(key=lambda item: item[0])
            return [service for _, service in matches]

        geography_type = Geography(geometry_type="POINT", srid=4326)
        reference_point = cast(func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326), geography_type)
        provider_location = cast(UserProfileModel.location, geography_type)
        distance_meters = radius_km * 1000.0

        stmt = (
            select(ServiceModel)
            .join(UserProfileModel, ServiceModel.provider_id == UserProfileModel.id)
            .where(ServiceModel.is_active.is_(True))
            .where(UserProfileModel.location.is_not(None))
            .where(func.ST_DWithin(provider_location, reference_point, distance_meters))
            .order_by(func.ST_Distance(provider_location, reference_point))
        )
        result = await self._session.execute(stmt)
        return [self._to_domain(model) for model in result.scalars().all()]

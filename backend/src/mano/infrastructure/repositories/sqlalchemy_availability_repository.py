"""SQLAlchemy implementation of AvailabilityRepository for DDD architecture."""

from __future__ import annotations

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from mano.common.uuid_utils import uuid_to_str
from mano.domain.models.availability import Availability, AvailabilityId
from mano.domain.models.service_model import ProviderId
from mano.domain.repositories.availability_repository import AvailabilityRepository
from mano.infrastructure.database.models import AvailabilityModel


class SQLAlchemyAvailabilityRepository(AvailabilityRepository):
    """SQLAlchemy implementation of the AvailabilityRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    @staticmethod
    def _to_domain(model: AvailabilityModel) -> Availability:
        """Convert database model to domain entity."""
        return Availability(
            id=AvailabilityId(str(model.id)),
            provider_id=ProviderId(str(model.provider_id)),
            day_of_week=model.day_of_week,
            start_time=model.start_time,
            end_time=model.end_time,
            is_available=model.is_available,
            specific_date=model.specific_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _apply_domain_to_model(domain: Availability, model: AvailabilityModel) -> None:
        """Apply domain model changes to database model."""
        model.provider_id = uuid_to_str(domain.provider_id)
        model.day_of_week = domain.day_of_week
        model.start_time = domain.start_time
        model.end_time = domain.end_time
        model.is_available = domain.is_available
        model.specific_date = domain.specific_date
        model.updated_at = domain.updated_at

    async def create_availability(self, availability: Availability) -> Availability:
        """Create a new availability slot."""
        model = AvailabilityModel(
            id=uuid_to_str(availability.id),
            provider_id=uuid_to_str(availability.provider_id),
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_available=availability.is_available,
            specific_date=availability.specific_date,
            created_at=availability.created_at,
            updated_at=availability.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_availability_by_id(self, availability_id: AvailabilityId) -> Availability | None:
        """Get availability by ID."""
        stmt = select(AvailabilityModel).where(AvailabilityModel.id == uuid_to_str(availability_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_provider(self, provider_id: ProviderId) -> list[Availability]:
        """List availability slots for a provider."""
        stmt = select(AvailabilityModel).where(AvailabilityModel.provider_id == uuid_to_str(provider_id))
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def list_all(self) -> list[Availability]:
        """List all availability slots."""
        stmt = select(AvailabilityModel)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def update_availability(self, availability: Availability) -> Availability:
        """Update an existing availability slot."""
        stmt = select(AvailabilityModel).where(AvailabilityModel.id == uuid_to_str(availability.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Availability with ID {availability.id} not found.")

        self._apply_domain_to_model(availability, model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete_availability(self, availability_id: AvailabilityId) -> None:
        """Delete an availability slot."""
        stmt = delete(AvailabilityModel).where(AvailabilityModel.id == uuid_to_str(availability_id))
        await self._session.execute(stmt)

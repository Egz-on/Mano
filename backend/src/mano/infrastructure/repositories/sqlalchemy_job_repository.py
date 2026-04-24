"""SQLAlchemy implementation of the job repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely import wkt
from shapely.geometry import Point
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from mano.common.uuid_utils import uuid_to_str
from mano.domain.exceptions.base import JobNotFoundError
from mano.domain.models.job import Job, JobId
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId
from mano.domain.repositories.job_repository import JobRepository
from mano.infrastructure.database.models import JobModel


class SQLAlchemyJobRepository(JobRepository):
    """Persist jobs using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _coordinates_from_location(raw_location: WKBElement | str | None) -> tuple[float, float]:
        if raw_location is None:
            raise ValueError("Job location cannot be null")
        point = to_shape(raw_location) if isinstance(raw_location, WKBElement) else wkt.loads(raw_location)
        return float(point.y), float(point.x)

    def _location_from_coordinates(self, latitude: float, longitude: float) -> Any:
        point = Point(longitude, latitude)
        bind = self._session.bind
        if bind is not None and bind.dialect.name == "sqlite":
            return point.wkt
        return from_shape(point, srid=4326)

    @classmethod
    def _to_domain(cls, model: JobModel) -> Job:
        latitude, longitude = cls._coordinates_from_location(model.location)
        return Job(
            id=JobId(str(model.id)),
            customer_id=UserId(str(model.customer_id)),
            technician_id=UserId(str(model.technician_id)) if model.technician_id else None,
            category_id=CategoryId(str(model.category_id)),
            description=cast(str, model.description),
            photo_urls=cast(list[str], model.photo_urls or []),
            latitude=latitude,
            longitude=longitude,
            address=cast(str, model.address),
            status=cast(str, model.status),
            call_out_fee_paid=cast(bool, model.call_out_fee_paid),
            chat_unlocked=cast(bool, model.chat_unlocked),
            quote_amount=cast(str | None, model.quote_amount),
            quote_description=cast(str | None, model.quote_description),
            quote_submitted_at=cast(datetime | None, model.quote_submitted_at),
            quote_approved_at=cast(datetime | None, model.quote_approved_at),
            quote_rejected_at=cast(datetime | None, model.quote_rejected_at),
            created_at=cast(datetime, model.created_at),
            updated_at=cast(datetime, model.updated_at),
        )

    def _apply_domain_to_model(self, job: Job, model: JobModel) -> None:
        model.customer_id = uuid_to_str(job.customer_id)
        model.technician_id = uuid_to_str(job.technician_id) if job.technician_id else None
        model.category_id = uuid_to_str(job.category_id)
        model.description = job.description
        model.photo_urls = job.photo_urls
        model.location = self._location_from_coordinates(job.latitude, job.longitude)
        model.address = job.address
        model.status = job.status
        model.call_out_fee_paid = job.call_out_fee_paid
        model.chat_unlocked = job.chat_unlocked
        model.quote_amount = job.quote_amount
        model.quote_description = job.quote_description
        model.quote_submitted_at = job.quote_submitted_at
        model.quote_approved_at = job.quote_approved_at
        model.quote_rejected_at = job.quote_rejected_at
        model.updated_at = job.updated_at

    async def create_job(self, job: Job) -> Job:
        model = JobModel(
            id=uuid_to_str(job.id),
            customer_id=uuid_to_str(job.customer_id),
            technician_id=uuid_to_str(job.technician_id) if job.technician_id else None,
            category_id=uuid_to_str(job.category_id),
            description=job.description,
            photo_urls=job.photo_urls,
            location=self._location_from_coordinates(job.latitude, job.longitude),
            address=job.address,
            status=job.status,
            call_out_fee_paid=job.call_out_fee_paid,
            chat_unlocked=job.chat_unlocked,
            quote_amount=job.quote_amount,
            quote_description=job.quote_description,
            quote_submitted_at=job.quote_submitted_at,
            quote_approved_at=job.quote_approved_at,
            quote_rejected_at=job.quote_rejected_at,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_job_by_id(self, job_id: JobId) -> Job | None:
        stmt = select(JobModel).where(JobModel.id == uuid_to_str(job_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_job(self, job: Job) -> Job:
        stmt = select(JobModel).where(JobModel.id == uuid_to_str(job.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise JobNotFoundError(f"Job {job.id} not found")

        self._apply_domain_to_model(job, model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete_job(self, job_id: JobId) -> None:
        stmt = delete(JobModel).where(JobModel.id == uuid_to_str(job_id))
        await self._session.execute(stmt)

    async def list_jobs(
        self,
        *,
        customer_id: UserId | None = None,
        technician_id: UserId | None = None,
        status: str | None = None,
    ) -> list[Job]:
        stmt = select(JobModel)
        if customer_id is not None:
            stmt = stmt.where(JobModel.customer_id == uuid_to_str(customer_id))
        if technician_id is not None:
            stmt = stmt.where(JobModel.technician_id == uuid_to_str(technician_id))
        if status is not None:
            stmt = stmt.where(JobModel.status == status)
        stmt = stmt.order_by(JobModel.created_at.desc())

        result = await self._session.execute(stmt)
        return [self._to_domain(model) for model in result.scalars().all()]

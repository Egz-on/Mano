"""Job domain service."""

from __future__ import annotations

from mano.domain.exceptions.base import JobNotFoundError
from mano.domain.models.job import Job, JobId
from mano.domain.models.user import UserId
from mano.domain.repositories.job_repository import JobRepository


class JobService:
    """Application-facing domain logic for jobs."""

    def __init__(self, job_repository: JobRepository) -> None:
        self._job_repository = job_repository

    async def create_job(self, job: Job) -> Job:
        return await self._job_repository.create_job(job)

    async def get_job_by_id(self, job_id: JobId) -> Job:
        job = await self._job_repository.get_job_by_id(job_id)
        if job is None:
            raise JobNotFoundError(f"Job {job_id} not found")
        return job

    async def update_job(self, job: Job) -> Job:
        return await self._job_repository.update_job(job)

    async def delete_job(self, job_id: JobId) -> None:
        await self.get_job_by_id(job_id)
        await self._job_repository.delete_job(job_id)

    async def list_jobs(
        self,
        *,
        customer_id: UserId | None = None,
        technician_id: UserId | None = None,
        status: str | None = None,
    ) -> list[Job]:
        return await self._job_repository.list_jobs(
            customer_id=customer_id,
            technician_id=technician_id,
            status=status,
        )

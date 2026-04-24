"""Job repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mano.domain.models.job import Job, JobId
from mano.domain.models.user import UserId


class JobRepository(ABC):
    """Abstract job repository."""

    @abstractmethod
    async def create_job(self, job: Job) -> Job:
        """Persist a new job."""

    @abstractmethod
    async def get_job_by_id(self, job_id: JobId) -> Job | None:
        """Return a job by id."""

    @abstractmethod
    async def update_job(self, job: Job) -> Job:
        """Persist an updated job aggregate."""

    @abstractmethod
    async def delete_job(self, job_id: JobId) -> None:
        """Delete a job by id."""

    @abstractmethod
    async def list_jobs(
        self,
        *,
        customer_id: UserId | None = None,
        technician_id: UserId | None = None,
        status: str | None = None,
    ) -> list[Job]:
        """List jobs matching the provided filters."""

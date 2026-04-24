"""Job use cases."""

from __future__ import annotations

from mano.application.dtos.job_dtos import (
    AssignTechnicianRequest,
    CreateJobRequest,
    JobResponseDTO,
    SubmitQuoteRequest,
    UpdateJobRequest,
)
from mano.domain.models.job import Job, JobId
from mano.domain.models.user import UserId
from mano.domain.services.job_service import JobService


class JobUseCases:
    """Application use cases for jobs."""

    def __init__(self, job_service: JobService) -> None:
        self._job_service = job_service

    async def create_job(self, request: CreateJobRequest) -> Job:
        """Create a new job from the given request."""
        job = Job.create(
            customer_id=request.customer_id,
            category_id=request.category_id,
            description=request.description,
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            photo_urls=request.photo_urls,
        )
        return await self._job_service.create_job(job)

    async def get_job_by_id(self, job_id: str) -> Job:
        """Retrieve a job by its ID."""
        return await self._job_service.get_job_by_id(JobId(job_id))

    async def update_job(self, job_id: str, request: UpdateJobRequest) -> Job:
        """Update job details."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.update(
            category_id=request.category_id,
            description=request.description,
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            photo_urls=request.photo_urls,
        )
        return await self._job_service.update_job(updated_job)

    async def delete_job(self, job_id: str) -> None:
        """Delete a job by ID."""
        await self._job_service.delete_job(JobId(job_id))

    async def list_jobs(
        self,
        *,
        customer_id: str | None = None,
        technician_id: str | None = None,
        status: str | None = None,
    ) -> list[JobResponseDTO]:
        """List jobs with optional filters."""
        jobs = await self._job_service.list_jobs(
            customer_id=UserId(customer_id) if customer_id else None,
            technician_id=UserId(technician_id) if technician_id else None,
            status=status,
        )
        return [JobResponseDTO.from_domain(job) for job in jobs]

    async def assign_technician(self, job_id: str, request: AssignTechnicianRequest) -> Job:
        """Assign a technician to a pending job."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.assign_technician(request.technician_id)
        return await self._job_service.update_job(updated_job)

    async def submit_quote(self, job_id: str, request: SubmitQuoteRequest) -> Job:
        """Submit a quote for a diagnosed job."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.submit_quote(amount=request.amount, description=request.description)
        return await self._job_service.update_job(updated_job)

    async def approve_quote(self, job_id: str) -> Job:
        """Approve the submitted quote."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.approve_quote()
        return await self._job_service.update_job(updated_job)

    async def reject_quote(self, job_id: str) -> Job:
        """Reject the submitted quote."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.reject_quote()
        return await self._job_service.update_job(updated_job)

    async def change_status(self, job_id: str, status: str) -> Job:
        """Transition a job to a new lifecycle status."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.change_status(status)
        return await self._job_service.update_job(updated_job)

    async def unlock_chat(self, job_id: str) -> Job:
        """Unlock chat for a job after call-out fee payment."""
        job = await self._job_service.get_job_by_id(JobId(job_id))
        updated_job = job.unlock_chat()
        return await self._job_service.update_job(updated_job)

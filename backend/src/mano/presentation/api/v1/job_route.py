"""Job API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mano.application.dtos.job_dtos import (
    AssignTechnicianRequest,
    CreateJobRequest,
    SubmitQuoteRequest,
    UpdateJobRequest,
)
from mano.application.use_cases.job_use_cases import JobUseCases
from mano.dependencies import get_current_user, get_job_use_cases
from mano.domain.exceptions.base import DomainError, JobNotFoundError, JobStateError
from mano.domain.models.job import Job, JobStatus
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId, UserProfile
from mano.presentation.schemas.job_schemas import (
    AssignTechnicianSchema,
    CreateJobSchema,
    JobResponseSchema,
    SubmitQuoteSchema,
    UpdateJobSchema,
    UpdateJobStatusSchema,
)
from mano.utils.pagination import PaginatedResponse, Pagination, PaginationParams

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_response(job: Job) -> JobResponseSchema:
    """Convert a Job domain entity to a response schema."""
    return JobResponseSchema.model_validate(job.to_dict())


def _is_job_customer(current_user: UserProfile, job: Job) -> bool:
    """Check if the current user is the job's customer."""
    return str(current_user.id) == str(job.customer_id)


def _is_job_technician(current_user: UserProfile, job: Job) -> bool:
    """Check if the current user is the job's assigned technician."""
    return job.technician_id is not None and str(current_user.id) == str(job.technician_id)


def _ensure_can_view_job(current_user: UserProfile, job: Job) -> None:
    """Raise 403 if the user cannot view the job."""
    if current_user.is_admin() or _is_job_customer(current_user, job) or _is_job_technician(current_user, job):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this job")


def _ensure_can_create_job(current_user: UserProfile, customer_id: UserId) -> None:
    """Raise 403 if the user cannot create a job for the given customer."""
    if current_user.is_admin():
        return
    if not current_user.is_client():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only clients can create jobs")
    if str(current_user.id) != str(customer_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create jobs for another customer")


def _ensure_can_manage_job(current_user: UserProfile, job: Job) -> None:
    """Raise 403 if the user cannot manage (update/delete) the job."""
    if current_user.is_admin() or _is_job_customer(current_user, job):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the customer can manage this job")


def _ensure_can_submit_quote(current_user: UserProfile, job: Job) -> None:
    """Raise 403 if the user cannot submit a quote for the job."""
    if current_user.is_admin() or _is_job_technician(current_user, job):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned technician can submit a quote")


def _ensure_can_change_status(current_user: UserProfile, job: Job, target_status: str) -> None:
    """Raise 403 if the user cannot transition the job to the target status."""
    if current_user.is_admin():
        return

    if target_status == JobStatus.cancelled.value:
        if _is_job_customer(current_user, job) or _is_job_technician(current_user, job):
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot cancel this job")

    if _is_job_technician(current_user, job):
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned technician can update status")


@router.post("/", response_model=JobResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: CreateJobSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Create a new job."""
    customer_id = UserId(str(payload.customer_id))
    _ensure_can_create_job(current_user, customer_id)

    request = CreateJobRequest(
        customer_id=customer_id,
        category_id=CategoryId(str(payload.category_id)),
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address=payload.address,
        photo_urls=payload.photo_urls,
    )
    try:
        job = await use_cases.create_job(request)
        return _to_response(job)
    except DomainError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{job_id}", response_model=JobResponseSchema)
async def get_job(
    job_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Retrieve a job by ID."""
    try:
        job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_view_job(current_user, job)
        return _to_response(job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/", response_model=PaginatedResponse[JobResponseSchema])
async def list_jobs(
    params: PaginationParams = Depends(PaginationParams.from_query),
    customer_id: UUID | None = Query(default=None),
    technician_id: UUID | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> PaginatedResponse[JobResponseSchema]:
    """List jobs with optional filters and role-based scoping."""
    scoped_customer_id = str(customer_id) if customer_id else None
    scoped_technician_id = str(technician_id) if technician_id else None

    if not current_user.is_admin():
        if current_user.is_client():
            scoped_customer_id = str(current_user.id)
            if customer_id and scoped_customer_id != str(customer_id):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another customer's jobs")
        elif current_user.is_provider():
            scoped_technician_id = str(current_user.id)
            if technician_id and scoped_technician_id != str(technician_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Cannot view another technician's jobs"
                )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unsupported role for job listing")

    jobs = await use_cases.list_jobs(
        customer_id=scoped_customer_id,
        technician_id=scoped_technician_id,
        status=status_filter,
    )
    return Pagination.paginate_items(
        [
            JobResponseSchema(
                id=UUID(dto.id),
                customer_id=UUID(dto.customer_id),
                technician_id=UUID(dto.technician_id) if dto.technician_id else None,
                category_id=UUID(dto.category_id),
                description=dto.description,
                photo_urls=dto.photo_urls,
                latitude=dto.latitude,
                longitude=dto.longitude,
                address=dto.address,
                status=dto.status,
                call_out_fee_paid=dto.call_out_fee_paid,
                chat_unlocked=dto.chat_unlocked,
                quote_amount=dto.quote_amount,
                quote_description=dto.quote_description,
                quote_submitted_at=dto.quote_submitted_at,
                quote_approved_at=dto.quote_approved_at,
                quote_rejected_at=dto.quote_rejected_at,
                created_at=dto.created_at,
                updated_at=dto.updated_at,
            )
            for dto in jobs
        ],
        params,
    )


@router.patch("/{job_id}", response_model=JobResponseSchema)
async def update_job(
    job_id: UUID,
    payload: UpdateJobSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Update an existing job's details."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_manage_job(current_user, existing_job)
        updated_job = await use_cases.update_job(
            str(job_id),
            UpdateJobRequest(
                category_id=CategoryId(str(payload.category_id)) if payload.category_id else None,
                description=payload.description,
                latitude=payload.latitude,
                longitude=payload.longitude,
                address=payload.address,
                photo_urls=payload.photo_urls,
            ),
        )
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (DomainError, JobStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> None:
    """Delete a job by ID."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_manage_job(current_user, existing_job)
        await use_cases.delete_job(str(job_id))
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{job_id}/assign", response_model=JobResponseSchema)
async def assign_technician(
    job_id: UUID,
    payload: AssignTechnicianSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Assign a technician to a pending job."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_manage_job(current_user, existing_job)
        updated_job = await use_cases.assign_technician(
            str(job_id),
            AssignTechnicianRequest(technician_id=UserId(str(payload.technician_id))),
        )
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (DomainError, JobStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{job_id}/quote", response_model=JobResponseSchema)
async def submit_quote(
    job_id: UUID,
    payload: SubmitQuoteSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Submit a quote for a diagnosed job."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_submit_quote(current_user, existing_job)
        updated_job = await use_cases.submit_quote(
            str(job_id),
            SubmitQuoteRequest(amount=payload.amount, description=payload.description),
        )
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (DomainError, JobStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{job_id}/quote/approve", response_model=JobResponseSchema)
async def approve_quote(
    job_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Approve the submitted quote for a job."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_manage_job(current_user, existing_job)
        updated_job = await use_cases.approve_quote(str(job_id))
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except JobStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{job_id}/quote/reject", response_model=JobResponseSchema)
async def reject_quote(
    job_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Reject the submitted quote for a job."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_manage_job(current_user, existing_job)
        updated_job = await use_cases.reject_quote(str(job_id))
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except JobStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/{job_id}/status", response_model=JobResponseSchema)
async def change_job_status(
    job_id: UUID,
    payload: UpdateJobStatusSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: JobUseCases = Depends(get_job_use_cases),
) -> JobResponseSchema:
    """Transition a job to a new lifecycle status."""
    try:
        existing_job = await use_cases.get_job_by_id(str(job_id))
        _ensure_can_change_status(current_user, existing_job, payload.status)
        updated_job = await use_cases.change_status(str(job_id), payload.status)
        return _to_response(updated_job)
    except JobNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except JobStateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

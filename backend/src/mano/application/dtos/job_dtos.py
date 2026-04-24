"""Job application DTOs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from mano.domain.models.job import Job
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId


@dataclass(frozen=True)
class CreateJobRequest:
    """DTO for creating a job."""

    customer_id: UserId
    category_id: CategoryId
    description: str
    latitude: float
    longitude: float
    address: str
    photo_urls: list[str] | None = None


@dataclass(frozen=True)
class UpdateJobRequest:
    """DTO for updating job details."""

    category_id: CategoryId | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    address: str | None = None
    photo_urls: list[str] | None = None


@dataclass(frozen=True)
class AssignTechnicianRequest:
    """DTO for assigning a technician."""

    technician_id: UserId


@dataclass(frozen=True)
class SubmitQuoteRequest:
    """DTO for submitting a quote."""

    amount: str
    description: str


@dataclass(frozen=True)
class JobResponseDTO:
    """DTO for job responses."""

    id: str
    customer_id: str
    technician_id: str | None
    category_id: str
    description: str
    photo_urls: list[str]
    latitude: float
    longitude: float
    address: str
    status: str
    call_out_fee_paid: bool
    chat_unlocked: bool
    quote_amount: str | None
    quote_description: str | None
    quote_submitted_at: datetime | None
    quote_approved_at: datetime | None
    quote_rejected_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, job: Job) -> JobResponseDTO:
        return cls(
            id=str(job.id),
            customer_id=str(job.customer_id),
            technician_id=str(job.technician_id) if job.technician_id else None,
            category_id=str(job.category_id),
            description=job.description,
            photo_urls=job.photo_urls,
            latitude=job.latitude,
            longitude=job.longitude,
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

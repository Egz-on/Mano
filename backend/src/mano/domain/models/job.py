"""Job domain aggregate."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any
import uuid

from mano.domain.exceptions.base import DomainError, JobStateError
from mano.domain.models.service_model import CategoryId
from mano.domain.models.user import UserId


class JobStatus(StrEnum):
    """Supported job lifecycle states."""

    pending = "pending"
    assigned = "assigned"
    en_route = "en_route"
    arrived = "arrived"
    diagnosed = "diagnosed"
    quote_approved = "quote_approved"
    quote_rejected = "quote_rejected"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


@dataclass(frozen=True)
class JobId:
    """Job identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Job:
    """Job aggregate root."""

    id: JobId
    customer_id: UserId
    category_id: CategoryId
    description: str
    latitude: float
    longitude: float
    address: str
    technician_id: UserId | None = None
    photo_urls: list[str] = field(default_factory=list)
    status: str = JobStatus.pending.value
    call_out_fee_paid: bool = False
    chat_unlocked: bool = False
    quote_amount: str | None = None
    quote_description: str | None = None
    quote_submitted_at: datetime | None = None
    quote_approved_at: datetime | None = None
    quote_rejected_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        normalized_description = self.description.strip()
        normalized_address = self.address.strip()
        normalized_status = JobStatus(self.status).value
        normalized_photos = [url.strip() for url in self.photo_urls if url and url.strip()]

        if not normalized_description:
            raise DomainError("Job description is required")
        if len(normalized_description) < 10:
            raise DomainError("Job description must be at least 10 characters long")
        if not normalized_address:
            raise DomainError("Job address is required")
        if not -90 <= self.latitude <= 90:
            raise DomainError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise DomainError("Longitude must be between -180 and 180")
        if normalized_status not in {status.value for status in JobStatus}:
            raise DomainError(f"Unsupported job status: {self.status}")

        if self.status not in {JobStatus.pending.value, JobStatus.cancelled.value} and self.technician_id is None:
            raise DomainError("A technician is required once a job leaves pending state")

        if self.quote_amount is not None:
            self._validate_quote_amount(self.quote_amount)
            if not (self.quote_description and self.quote_description.strip()):
                raise DomainError("Quote description is required when a quote amount is provided")

        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "address", normalized_address)
        object.__setattr__(self, "status", normalized_status)
        object.__setattr__(self, "photo_urls", normalized_photos)
        if self.quote_description is not None:
            object.__setattr__(self, "quote_description", self.quote_description.strip())

    @classmethod
    def create(
        cls,
        *,
        customer_id: UserId,
        category_id: CategoryId,
        description: str,
        latitude: float,
        longitude: float,
        address: str,
        photo_urls: list[str] | None = None,
    ) -> Job:
        """Create a new job in the pending state."""
        now = datetime.now(UTC)
        return cls(
            id=JobId(),
            customer_id=customer_id,
            category_id=category_id,
            description=description,
            latitude=latitude,
            longitude=longitude,
            address=address,
            photo_urls=photo_urls or [],
            created_at=now,
            updated_at=now,
        )

    def update(
        self,
        *,
        category_id: CategoryId | None = None,
        description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        photo_urls: list[str] | None = None,
    ) -> Job:
        """Update mutable job details."""
        self._ensure_not_terminal("Only active jobs can be updated")
        return replace(
            self,
            category_id=category_id if category_id is not None else self.category_id,
            description=description if description is not None else self.description,
            latitude=latitude if latitude is not None else self.latitude,
            longitude=longitude if longitude is not None else self.longitude,
            address=address if address is not None else self.address,
            photo_urls=photo_urls if photo_urls is not None else self.photo_urls,
            updated_at=datetime.now(UTC),
        )

    def assign_technician(self, technician_id: UserId) -> Job:
        """Assign or reassign a technician to the job."""
        self._ensure_not_terminal("Cannot assign a technician to a closed job")
        return replace(
            self,
            technician_id=technician_id,
            status=JobStatus.assigned.value,
            updated_at=datetime.now(UTC),
        )

    def submit_quote(self, *, amount: str, description: str) -> Job:
        """Attach a quote to a diagnosed job."""
        self._ensure_not_terminal("Cannot submit a quote for a closed job")
        if self.technician_id is None:
            raise JobStateError("A technician must be assigned before submitting a quote")

        normalized_amount = self._validate_quote_amount(amount)
        normalized_description = description.strip()
        if not normalized_description:
            raise DomainError("Quote description is required")

        now = datetime.now(UTC)
        return replace(
            self,
            status=JobStatus.diagnosed.value,
            quote_amount=normalized_amount,
            quote_description=normalized_description,
            quote_submitted_at=now,
            quote_approved_at=None,
            quote_rejected_at=None,
            updated_at=now,
        )

    def approve_quote(self) -> Job:
        """Approve the current quote and unlock the chat."""
        if self.quote_amount is None:
            raise JobStateError("Cannot approve a quote that has not been submitted")
        if self.status != JobStatus.diagnosed.value:
            raise JobStateError("Only diagnosed jobs with a submitted quote can be approved")

        now = datetime.now(UTC)
        return replace(
            self,
            status=JobStatus.quote_approved.value,
            call_out_fee_paid=True,
            chat_unlocked=True,
            quote_approved_at=now,
            updated_at=now,
        )

    def reject_quote(self) -> Job:
        """Reject the current quote."""
        if self.quote_amount is None:
            raise JobStateError("Cannot reject a quote that has not been submitted")
        if self.status != JobStatus.diagnosed.value:
            raise JobStateError("Only diagnosed jobs with a submitted quote can be rejected")

        now = datetime.now(UTC)
        return replace(
            self,
            status=JobStatus.quote_rejected.value,
            quote_rejected_at=now,
            updated_at=now,
        )

    def unlock_chat(self) -> Job:
        """Unlock the chat for the job."""
        return replace(self, chat_unlocked=True, updated_at=datetime.now(UTC))

    def change_status(self, status: str) -> Job:
        """Move the job through its lifecycle."""
        target_status = JobStatus(status).value
        allowed_transitions = {
            JobStatus.pending.value: {JobStatus.assigned.value, JobStatus.cancelled.value},
            JobStatus.assigned.value: {
                JobStatus.en_route.value,
                JobStatus.arrived.value,
                JobStatus.diagnosed.value,
                JobStatus.cancelled.value,
            },
            JobStatus.en_route.value: {JobStatus.arrived.value, JobStatus.cancelled.value},
            JobStatus.arrived.value: {
                JobStatus.diagnosed.value,
                JobStatus.in_progress.value,
                JobStatus.cancelled.value,
            },
            JobStatus.diagnosed.value: {
                JobStatus.quote_approved.value,
                JobStatus.quote_rejected.value,
                JobStatus.cancelled.value,
            },
            JobStatus.quote_approved.value: {JobStatus.in_progress.value, JobStatus.cancelled.value},
            JobStatus.quote_rejected.value: {JobStatus.assigned.value, JobStatus.cancelled.value},
            JobStatus.in_progress.value: {JobStatus.completed.value, JobStatus.cancelled.value},
            JobStatus.completed.value: set(),
            JobStatus.cancelled.value: set(),
        }

        if target_status == self.status:
            return self

        if target_status not in allowed_transitions[self.status]:
            raise JobStateError(f"Cannot transition job from {self.status} to {target_status}")

        if target_status not in {JobStatus.cancelled.value} and self.technician_id is None:
            raise JobStateError("A technician must be assigned before progressing the job")

        return replace(self, status=target_status, updated_at=datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Serialize the aggregate for API responses."""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "technician_id": str(self.technician_id) if self.technician_id else None,
            "category_id": str(self.category_id),
            "description": self.description,
            "photo_urls": self.photo_urls,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "status": self.status,
            "call_out_fee_paid": self.call_out_fee_paid,
            "chat_unlocked": self.chat_unlocked,
            "quote_amount": self.quote_amount,
            "quote_description": self.quote_description,
            "quote_submitted_at": self.quote_submitted_at.isoformat() if self.quote_submitted_at else None,
            "quote_approved_at": self.quote_approved_at.isoformat() if self.quote_approved_at else None,
            "quote_rejected_at": self.quote_rejected_at.isoformat() if self.quote_rejected_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def _ensure_not_terminal(self, message: str) -> None:
        if self.status in {JobStatus.completed.value, JobStatus.cancelled.value}:
            raise JobStateError(message)

    @staticmethod
    def _validate_quote_amount(amount: str) -> str:
        normalized_amount = amount.strip()
        if not normalized_amount:
            raise DomainError("Quote amount is required")
        try:
            decimal_amount = Decimal(normalized_amount)
        except InvalidOperation as exc:
            raise DomainError("Quote amount must be a valid decimal number") from exc
        if decimal_amount <= 0:
            raise DomainError("Quote amount must be greater than zero")
        return format(decimal_amount.normalize(), "f")

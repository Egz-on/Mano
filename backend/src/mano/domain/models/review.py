"""Review domain entity."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
import uuid

from mano.domain.exceptions.review_exceptions import ReviewValidationError
from mano.domain.models.service_model import ServiceId
from mano.domain.models.user import UserId


@dataclass(frozen=True)
class ReviewId:
    """Service identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of ServiceId."""
        return self.value


@dataclass(frozen=True)
class ClientId:
    """Service identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of ServiceId."""
        return self.value


@dataclass(frozen=True)
class ProviderId:
    """Service identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of ServiceId."""
        return self.value


@dataclass(frozen=True)
class Review:
    """Review domain entity."""

    id: ReviewId
    client_id: ClientId
    provider_id: ProviderId
    service_id: ServiceId
    rating: int
    comment: str | None = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    moderated_by: UserId | None = None
    moderated_at: datetime | None = None
    guest_name: str | None = None
    guest_email: str | None = None
    moderation_notes: str | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.rating <= 5:
            raise ReviewValidationError("Rating must be between 1 and 5")

        if not self.comment or not self.comment.strip():
            raise ReviewValidationError("Comment cannot be empty")

        if len(self.comment.strip()) > 1000:
            raise ReviewValidationError("Comment must be 1000 characters or less")

        normalized_status = ReviewStatus(self.status).value
        object.__setattr__(self, "status", normalized_status)
        object.__setattr__(self, "comment", self.comment.strip())

        if self.client_id.value == self.provider_id.value:
            raise ReviewValidationError("Client cannot review their own service")

        if self.guest_name is not None:
            guest_name = self.guest_name.strip()
            if not guest_name:
                raise ReviewValidationError("Guest name cannot be empty")
            object.__setattr__(self, "guest_name", guest_name)

        if self.guest_email is not None:
            guest_email = self.guest_email.strip().lower()
            if "@" not in guest_email:
                raise ReviewValidationError("Guest email is invalid")
            object.__setattr__(self, "guest_email", guest_email)

    @classmethod
    def create(
        cls,
        client_id: ClientId,
        provider_id: ProviderId,
        service_id: ServiceId,
        rating: int,
        comment: str,
    ) -> "Review":
        """Create a new Review with validation."""
        now = datetime.now(UTC)

        return cls(
            id=ReviewId(),
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=rating,
            comment=comment,
            status=ReviewStatus.pending.value,
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_public(
        cls,
        *,
        client_id: ClientId,
        provider_id: ProviderId,
        service_id: ServiceId,
        rating: int,
        comment: str,
        guest_name: str | None = None,
        guest_email: str | None = None,
        status: str = "approved",
    ) -> "Review":
        """Create a public review from an authenticated or guest client."""
        now = datetime.now(UTC)
        return cls(
            id=ReviewId(),
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=rating,
            comment=comment,
            guest_name=guest_name,
            guest_email=guest_email,
            status=status,
            created_at=now,
            updated_at=now,
        )

    def update_content(self, *, rating: int | None = None, comment: str | None = None) -> "Review":
        """Return a new review with updated review content."""
        return replace(
            self,
            rating=rating if rating is not None else self.rating,
            comment=comment if comment is not None else self.comment,
            updated_at=datetime.now(UTC),
        )

    def approve(self, *, moderated_by: UserId | None = None, moderation_notes: str | None = None) -> "Review":
        """Mark the review as approved."""
        return replace(
            self,
            status=ReviewStatus.approved.value,
            moderated_by=moderated_by,
            moderation_notes=moderation_notes,
            moderated_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    def reject(self, *, moderated_by: UserId | None = None, moderation_notes: str | None = None) -> "Review":
        """Mark the review as rejected."""
        return replace(
            self,
            status=ReviewStatus.rejected.value,
            moderated_by=moderated_by,
            moderation_notes=moderation_notes,
            moderated_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class CreateReviewRequest:
    """DTO for creating a new review."""

    client_id: ClientId
    provider_id: ProviderId
    service_id: ServiceId
    rating: int
    comment: str


class ReviewStatus(StrEnum):
    """Allowed moderation states for reviews."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"

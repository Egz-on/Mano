"""Review domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
import uuid
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
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        if not comment or not comment.strip():
            raise ValueError("Comment cannot be empty")

        if len(comment.strip()) > 1000:
            raise ValueError("Comment must be 1000 characters or less")

        if client_id.value == provider_id.value:
            raise ValueError("Client cannot review their own service")

        now = datetime.now()

        return cls(
            id=ReviewId(),
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=rating,
            comment=comment,
            status="PENDING",
            created_at=now,
            updated_at=now,
        )


@dataclass(frozen=True)
class CreateReviewRequest:
    """DTO for creating a new review."""

    client_id: ClientId
    provider_id: ProviderId
    service_id: ServiceId
    rating: int
    comment: str

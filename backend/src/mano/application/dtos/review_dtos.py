"""Application DTOs for review workflows."""

from dataclasses import dataclass
from mano.domain.models.review import ClientId, ProviderId, ReviewId
from mano.domain.models.service_model import ServiceId


@dataclass(frozen=True)
class CreatePublicReviewCommand:
    provider_id: str
    service_id: str
    rating: int
    comment: str | None = None
    client_id: str | None = None


@dataclass(frozen=True)
class CreateReviewRequest:
    """Application request for creating a review."""

    client_id: ClientId
    provider_id: ProviderId
    service_id: ServiceId
    rating: int
    comment: str


@dataclass(frozen=True)
class UpdateReviewRequest:
    """Application request for updating a review."""

    review_id: ReviewId
    rating: int | None = None
    comment: str | None = None

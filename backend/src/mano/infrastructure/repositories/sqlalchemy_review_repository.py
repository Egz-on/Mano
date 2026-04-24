"""SQLAlchemy implementation of ReviewRepository for DDD architecture."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from mano.common.uuid_utils import uuid_to_str
from mano.domain.exceptions.review_exceptions import ReviewNotFound
from mano.domain.models.review import ClientId, ProviderId, Review, ReviewId
from mano.domain.models.service_model import ServiceId
from mano.domain.models.user import UserId
from mano.domain.repositories.review_repository import ReviewRepository
from mano.infrastructure.database.models import ReviewModel


class SQLAlchemyReviewRepository(ReviewRepository):
    """SQLAlchemy implementation of the ReviewRepository interface."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self._session = session

    # =====================
    # Mapping helpers
    # =====================

    @staticmethod
    def _to_domain(model: ReviewModel) -> Review:
        """Convert database model to domain entity."""
        return Review(
            id=ReviewId(str(model.id)),
            client_id=ClientId(str(model.client_id)),
            provider_id=ProviderId(str(model.provider_id)),
            service_id=ServiceId(str(model.service_id)),
            rating=model.rating,
            comment=model.comment,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            moderated_by=UserId(str(model.moderated_by)) if model.moderated_by else None,
            moderated_at=model.moderated_at,
            moderation_notes=model.moderation_notes,
        )

    # =====================
    # Repository methods
    # =====================

    async def add_review(self, review: Review) -> Review:
        """Create a new review."""
        model = ReviewModel(
            id=uuid_to_str(review.id),
            client_id=uuid_to_str(review.client_id),
            provider_id=uuid_to_str(review.provider_id),
            service_id=uuid_to_str(review.service_id),
            rating=review.rating,
            comment=review.comment,
            status=review.status,
            created_at=review.created_at,
            updated_at=review.updated_at,
            moderated_by=uuid_to_str(review.moderated_by) if review.moderated_by else None,
            moderated_at=review.moderated_at,
            moderation_notes=review.moderation_notes,
        )
        self._session.add(model)
        await self._session.flush()  # Ensure the model gets persisted
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, review_id: ReviewId) -> Review | None:
        """Get review by ID."""
        stmt = select(ReviewModel).where(ReviewModel.id == review_id.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def list_by_service(self, service_id: ServiceId) -> list[Review]:
        """List reviews for a service."""
        stmt = select(ReviewModel).where(ReviewModel.service_id == service_id.value)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def update(self, review: Review) -> Review:
        """Update a review."""
        stmt = select(ReviewModel).where(ReviewModel.id == uuid_to_str(review.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ReviewNotFound(f"Review with ID {review.id} not found")

        model.client_id = uuid_to_str(review.client_id)
        model.provider_id = uuid_to_str(review.provider_id)
        model.service_id = uuid_to_str(review.service_id)
        model.rating = review.rating
        model.comment = review.comment
        model.status = review.status
        model.created_at = review.created_at
        model.updated_at = review.updated_at
        model.moderated_by = uuid_to_str(review.moderated_by) if review.moderated_by else None
        model.moderated_at = review.moderated_at
        model.moderation_notes = review.moderation_notes
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete(self, review_id: ReviewId) -> None:
        """Delete a review."""
        stmt = delete(ReviewModel).where(ReviewModel.id == review_id.value)
        await self._session.execute(stmt)
        await self._session.flush()

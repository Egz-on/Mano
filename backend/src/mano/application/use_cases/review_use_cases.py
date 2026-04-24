"""Review use cases module."""

from __future__ import annotations


from mano.application.dtos.review_dtos import CreatePublicReviewCommand, CreateReviewRequest, UpdateReviewRequest
from mano.domain.exceptions.review_exceptions import ReviewNotFound, ReviewValidationError
from mano.domain.models.review import ClientId, ProviderId, Review, ReviewId
from mano.domain.models.service_model import ServiceId
from mano.domain.services.rating_service import RatingService
from mano.domain.services.review_service import ReviewService
from mano.domain.services.user_service import UserService


class ReviewUseCases:
    """Application use cases for reviews."""

    def __init__(
        self,
        review_service: ReviewService,
        rating_service: RatingService,
        user_service: UserService,
    ) -> None:
        self.review_service = review_service
        self.rating_service = rating_service
        self.user_service = user_service

    async def create_public_review(self, command: CreatePublicReviewCommand) -> Review:
        """Create a review from authenticated client."""
        client_id = command.client_id
        if not client_id:
            raise ReviewValidationError("client_id is required")

        review = Review.create_public(
            client_id=ClientId(client_id),
            provider_id=ProviderId(command.provider_id),
            service_id=ServiceId(command.service_id),
            rating=command.rating,
            comment=command.comment or "",
        )
        created = await self.review_service.create_review(review)
        await self.rating_service.recalculate_average_rating(ServiceId(command.service_id))
        return created

    async def create_review(self, request: CreateReviewRequest) -> Review:
        """Create a review from an internal application request."""
        review = Review.create(
            client_id=request.client_id,
            provider_id=request.provider_id,
            service_id=request.service_id,
            rating=request.rating,
            comment=request.comment,
        )
        created = await self.review_service.create_review(review)
        await self.rating_service.recalculate_average_rating(request.service_id)
        return created

    async def get_review(self, review_id: ReviewId) -> Review | None:
        """Get review by ID."""
        return await self.review_service.get_review(review_id)

    async def list_reviews_for_service(self, service_id: ServiceId) -> list[Review]:
        """List reviews for a service."""
        return await self.review_service.list_reviews(service_id)

    async def update_review(self, request: UpdateReviewRequest) -> Review:
        """Update an existing review."""
        existing = await self.review_service.get_review(request.review_id)
        if existing is None:
            raise ReviewNotFound(f"Review with ID {request.review_id} not found")

        updated = existing.update_content(rating=request.rating, comment=request.comment)
        result = await self.review_service.update_review(updated)
        await self.rating_service.recalculate_average_rating(existing.service_id)
        return result

    async def delete_review(self, review_id: ReviewId) -> None:
        """Delete review and refresh parent service rating."""
        existing = await self.review_service.get_review(review_id)
        if existing is None:
            raise ReviewNotFound(f"Review with ID {review_id} not found")

        await self.review_service.delete_review(review_id)
        await self.rating_service.recalculate_average_rating(existing.service_id)

from mano.domain.models.review import Review, ReviewId
from mano.domain.models.service_model import ServiceId
from mano.domain.repositories.review_repository import ReviewRepository


class ReviewService:
    "Review domain service for business logic operations"

    def __init__(self, review_repository: ReviewRepository) -> None:
        """Initialize service with repository and image storage dependencies."""
        self.review_repository = review_repository

    async def create_review(self, review: Review) -> Review:
        """Create a new review."""
        return await self.review_repository.add_review(review)

    async def get_review(self, review_id: ReviewId) -> Review | None:
        """Get review by ID."""
        return await self.review_repository.get_by_id(review_id)

    async def list_reviews(self, service_id: ServiceId) -> list[Review]:
        """List reviews for a service."""
        return await self.review_repository.list_by_service(service_id)

    async def update_review(self, review: Review) -> Review:
        """Update a review."""
        return await self.review_repository.update(review)

    async def delete_review(self, review_id: ReviewId) -> None:
        """Delete a review."""
        return await self.review_repository.delete(review_id)

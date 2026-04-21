"""Rating domain service."""

from mano.domain.exceptions.base import ServiceNotFoundError
from mano.domain.models.review import ReviewStatus
from mano.domain.models.service_model import ServiceId, Service
from mano.domain.repositories.review_repository import ReviewRepository
from mano.domain.repositories.service_repository import ServiceRepository


class RatingService:
    """Service for managing rating calculations."""

    def __init__(
        self,
        review_repository: ReviewRepository,
        service_repository: ServiceRepository,
    ) -> None:
        """Initialize with repositories."""
        self.review_repository = review_repository
        self.service_repository = service_repository

    async def recalculate_average_rating(self, service_id: ServiceId) -> Service:
        """Recalculate average rating for a service based on approved reviews."""
        service = await self.service_repository.get_service_by_id(service_id)
        if not service:
            raise ServiceNotFoundError(f"Service {service_id} not found")

        reviews = [
            review
            for review in await self.review_repository.list_by_service(service_id)
            if review.status == ReviewStatus.approved.value
        ]

        count = len(reviews)
        if count == 0:
            avg_rating = 0.0
        else:
            total_score = sum(r.rating for r in reviews)
            avg_rating = round(total_score / count, 2)

        updated_service = service.update_stats(rating=avg_rating, review_count=count)
        return await self.service_repository.update_service(updated_service)

"""Review use cases module."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import NAMESPACE_DNS, uuid5

from workmate.application.dtos.review_dtos import CreatePublicReviewCommand, UpdateReviewRequest
from workmate.domain.exceptions.review_exceptions import ReviewNotFound
from workmate.domain.models.review import ClientId, ProviderId, Review, ReviewId
from workmate.domain.models.service_model import ServiceId
from workmate.domain.models.user import PhoneNumber, UserAuthId, UserId, UserProfile, UserRole
from workmate.domain.services.rating_service import RatingService
from workmate.domain.services.review_service import ReviewService
from workmate.domain.services.user_service import UserService


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
        """Create a review from authenticated client or guest reviewer."""
        client_id = command.client_id
        guest_name = command.guest_name.strip() if command.guest_name else None
        guest_email = command.guest_email.strip().lower() if command.guest_email else None

        if not client_id:
            if not guest_name or not guest_email:
                raise ValueError("Guest reviews require guest_name and guest_email")
            client_id = await self._get_or_create_guest_user_id(guest_name=guest_name, guest_email=guest_email)

        review = Review(
            id=ReviewId(),
            client_id=ClientId(client_id),
            provider_id=ProviderId(command.provider_id),
            service_id=ServiceId(command.service_id),
            rating=command.rating,
            comment=command.comment,
            guest_name=guest_name,
            guest_email=guest_email,
            status="approved",
        )
        created = await self.review_service.create_review(review)
        await self.rating_service.recalculate_average_rating(ServiceId(command.service_id))
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

        updated = Review(
            id=existing.id,
            client_id=existing.client_id,
            provider_id=existing.provider_id,
            service_id=existing.service_id,
            rating=request.rating if request.rating is not None else existing.rating,
            comment=request.comment if request.comment is not None else existing.comment,
            status=existing.status,
            created_at=existing.created_at,
            updated_at=datetime.now(UTC),
            moderated_by=existing.moderated_by,
            moderated_at=existing.moderated_at,
            guest_name=existing.guest_name,
            guest_email=existing.guest_email,
            moderation_notes=existing.moderation_notes,
        )
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

    async def _get_or_create_guest_user_id(self, *, guest_name: str, guest_email: str) -> str:
        users = await self.user_service.list_users()
        for user in users:
            email = (user.profile_metadata or {}).get("email")
            if isinstance(email, str) and email.strip().lower() == guest_email:
                return str(user.id)

        auth_user_id = UserAuthId(str(uuid5(NAMESPACE_DNS, f"workmate:guest:{guest_email}")))
        now = datetime.now(UTC)
        guest_user = UserProfile(
            id=UserId(),
            auth_user_id=auth_user_id,
            full_name=guest_name,
            phone=str(PhoneNumber("+38970000001")),
            role=UserRole.client,
            profile_metadata={"email": guest_email, "is_guest": True},
            created_at=now,
            updated_at=now,
        )
        created_user = await self.user_service.create_user_profile(guest_user)
        return str(created_user.id)
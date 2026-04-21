import pytest
from unittest.mock import AsyncMock
from workmate.domain.services.review_service import ReviewService
from workmate.domain.models.review import Review, ClientId, ProviderId, ReviewId
from workmate.domain.models.service_model import ServiceId
from workmate.domain.repositories.review_repository import ReviewRepository


class TestReviewService:
    @pytest.mark.asyncio
    async def test_create_review(self):
        mock_repo = AsyncMock(spec=ReviewRepository)
        service = ReviewService(review_repository=mock_repo)

        review = Review.create(
            client_id=ClientId(),
            provider_id=ProviderId(),
            service_id=ServiceId(),
            rating=5,
            comment="Great!",
        )

        mock_repo.add_review.return_value = review

        result = await service.create_review(review)

        mock_repo.add_review.assert_called_once_with(review)
        assert result == review

    @pytest.mark.asyncio
    async def test_get_review(self):
        mock_repo = AsyncMock(spec=ReviewRepository)
        service = ReviewService(review_repository=mock_repo)
        review_id = ReviewId()
        expected_review = AsyncMock(spec=Review)
        mock_repo.get_by_id.return_value = expected_review

        result = await service.get_review(review_id)

        mock_repo.get_by_id.assert_called_once_with(review_id)
        assert result == expected_review

    @pytest.mark.asyncio
    async def test_list_reviews(self):
        mock_repo = AsyncMock(spec=ReviewRepository)
        service = ReviewService(review_repository=mock_repo)
        service_id = ServiceId()
        expected_reviews = [AsyncMock(spec=Review)]
        mock_repo.list_by_service.return_value = expected_reviews

        result = await service.list_reviews(service_id)

        mock_repo.list_by_service.assert_called_once_with(service_id)
        assert result == expected_reviews

    @pytest.mark.asyncio
    async def test_update_review(self):
        mock_repo = AsyncMock(spec=ReviewRepository)
        service = ReviewService(review_repository=mock_repo)
        review = AsyncMock(spec=Review)
        mock_repo.update.return_value = review

        result = await service.update_review(review)

        mock_repo.update.assert_called_once_with(review)
        assert result == review

    @pytest.mark.asyncio
    async def test_delete_review(self):
        mock_repo = AsyncMock(spec=ReviewRepository)
        service = ReviewService(review_repository=mock_repo)
        review_id = ReviewId()
        mock_repo.delete.return_value = None

        await service.delete_review(review_id)

        mock_repo.delete.assert_called_once_with(review_id)

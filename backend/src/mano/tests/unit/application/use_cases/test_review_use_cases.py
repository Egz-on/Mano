import pytest
from unittest.mock import AsyncMock
from mano.application.use_cases.review_use_cases import ReviewUseCases
from mano.application.dtos.review_dtos import CreateReviewRequest, UpdateReviewRequest
from mano.domain.services.review_service import ReviewService
from mano.domain.services.rating_service import RatingService
from mano.domain.services.user_service import UserService
from mano.domain.models.review import (
    Review,
    ClientId,
    ProviderId,
    ReviewId,
)
from mano.domain.models.service_model import ServiceId
from mano.domain.exceptions.review_exceptions import ReviewNotFound


class TestReviewUseCases:
    @pytest.fixture
    def mock_review_service(self):
        return AsyncMock(spec=ReviewService)

    @pytest.fixture
    def mock_rating_service(self):
        return AsyncMock(spec=RatingService)

    @pytest.fixture
    def mock_user_service(self):
        return AsyncMock(spec=UserService)

    @pytest.fixture
    def use_cases(self, mock_review_service, mock_rating_service, mock_user_service):
        return ReviewUseCases(
            review_service=mock_review_service,
            rating_service=mock_rating_service,
            user_service=mock_user_service,
        )

    @pytest.mark.asyncio
    async def test_create_review_use_case(self, use_cases, mock_review_service, mock_rating_service):
        client_id = ClientId()
        provider_id = ProviderId()
        service_id = ServiceId()
        request = CreateReviewRequest(
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=4,
            comment="Good work",
        )

        expected_review = Review.create(
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=4,
            comment="Good work",
        )
        mock_review_service.create_review.return_value = expected_review

        result = await use_cases.create_review(request)

        mock_review_service.create_review.assert_called_once()
        mock_rating_service.recalculate_average_rating.assert_called_once_with(service_id)
        assert result == expected_review

    @pytest.mark.asyncio
    async def test_get_review(self, use_cases, mock_review_service):
        review_id = ReviewId()
        expected = AsyncMock(spec=Review)
        mock_review_service.get_review.return_value = expected

        result = await use_cases.get_review(review_id)

        mock_review_service.get_review.assert_called_once_with(review_id)
        assert result == expected

    @pytest.mark.asyncio
    async def test_list_reviews_for_service(self, use_cases, mock_review_service):
        service_id = ServiceId()
        expected = [AsyncMock(spec=Review)]
        mock_review_service.list_reviews.return_value = expected

        result = await use_cases.list_reviews_for_service(service_id)

        mock_review_service.list_reviews.assert_called_once_with(service_id)
        assert result == expected

    @pytest.mark.asyncio
    async def test_update_review(self, use_cases, mock_review_service, mock_rating_service):
        # Setup existing review
        service_id = ServiceId()
        existing_review = Review.create(
            client_id=ClientId(), provider_id=ProviderId(), service_id=service_id, rating=4, comment="Original"
        )
        review_id = existing_review.id
        mock_review_service.get_review.return_value = existing_review

        updated_return = AsyncMock(spec=Review)
        updated_return.service_id = service_id
        mock_review_service.update_review.return_value = updated_return

        request = UpdateReviewRequest(review_id=review_id, rating=5, comment="Updated")

        result = await use_cases.update_review(request)

        mock_review_service.get_review.assert_called_with(review_id)
        mock_review_service.update_review.assert_called_once()
        mock_rating_service.recalculate_average_rating.assert_called_once_with(service_id)

        updated_arg = mock_review_service.update_review.call_args[0][0]
        assert updated_arg.rating == 5
        assert updated_arg.comment == "Updated"
        assert result == updated_return

    @pytest.mark.asyncio
    async def test_delete_review(self, use_cases, mock_review_service, mock_rating_service):
        review_id = ReviewId()
        service_id = ServiceId()
        existing_review = AsyncMock(spec=Review)
        existing_review.service_id = service_id
        mock_review_service.get_review.return_value = existing_review

        await use_cases.delete_review(review_id)

        mock_review_service.delete_review.assert_called_once_with(review_id)
        mock_rating_service.recalculate_average_rating.assert_called_once_with(service_id)

    @pytest.mark.asyncio
    async def test_update_review_not_found(self, use_cases, mock_review_service):
        review_id = ReviewId()
        mock_review_service.get_review.return_value = None
        request = UpdateReviewRequest(review_id=review_id, rating=5)

        with pytest.raises(ReviewNotFound):
            await use_cases.update_review(request)

    @pytest.mark.asyncio
    async def test_delete_review_not_found(self, use_cases, mock_review_service):
        review_id = ReviewId()
        mock_review_service.get_review.return_value = None

        with pytest.raises(ReviewNotFound):
            await use_cases.delete_review(review_id)

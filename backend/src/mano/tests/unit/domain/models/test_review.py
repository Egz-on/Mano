from datetime import datetime
import pytest
from mano.domain.models.review import Review, ClientId, ProviderId
from mano.domain.models.service_model import ServiceId
from mano.domain.exceptions.review_exceptions import ReviewValidationError


class TestReview:
    def test_create_review_success(self):
        client_id = ClientId()
        provider_id = ProviderId()
        service_id = ServiceId()
        rating = 5
        comment = "Excellent service!"

        review = Review.create(
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            rating=rating,
            comment=comment,
        )

        assert review.client_id == client_id
        assert review.provider_id == provider_id
        assert review.service_id == service_id
        assert review.rating == rating
        assert review.comment == comment
        assert review.status == "pending"
        assert isinstance(review.created_at, datetime)
        assert review.updated_at == review.created_at
        assert review.moderated_by is None

    def test_create_review_invalid_rating_low(self):
        with pytest.raises(ReviewValidationError, match="Rating must be between 1 and 5"):
            Review.create(
                client_id=ClientId(),
                provider_id=ProviderId(),
                service_id=ServiceId(),
                rating=0,
                comment="Bad",
            )

    def test_create_review_invalid_rating_high(self):
        with pytest.raises(ReviewValidationError, match="Rating must be between 1 and 5"):
            Review.create(
                client_id=ClientId(),
                provider_id=ProviderId(),
                service_id=ServiceId(),
                rating=6,
                comment="Too good",
            )

    def test_create_review_empty_comment(self):
        with pytest.raises(ReviewValidationError, match="Comment cannot be empty"):
            Review.create(
                client_id=ClientId(),
                provider_id=ProviderId(),
                service_id=ServiceId(),
                rating=5,
                comment="   ",
            )

    def test_create_review_long_comment(self):
        long_comment = "a" * 1001
        with pytest.raises(ReviewValidationError, match="Comment must be 1000 characters or less"):
            Review.create(
                client_id=ClientId(),
                provider_id=ProviderId(),
                service_id=ServiceId(),
                rating=5,
                comment=long_comment,
            )

    def test_create_review_self_review(self):
        c_id = ClientId(value="12345")
        p_id = ProviderId(value="12345")

        with pytest.raises(ReviewValidationError, match="Client cannot review their own service"):
            Review.create(
                client_id=c_id,
                provider_id=p_id,
                service_id=ServiceId(),
                rating=5,
                comment="Self review",
            )

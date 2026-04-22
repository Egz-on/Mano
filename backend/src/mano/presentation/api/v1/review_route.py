from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from mano.application.dtos.review_dtos import CreatePublicReviewCommand, UpdateReviewRequest
from mano.application.use_cases.review_use_cases import ReviewUseCases
from mano.dependencies import get_review_use_cases
from mano.domain.exceptions.review_exceptions import ReviewNotFound, ReviewValidationError
from mano.domain.models.review import (
    Review,
    ReviewId,
)
from mano.domain.models.service_model import ServiceId
from mano.presentation.schemas.review_schema import ReviewCreateSchema, ReviewResponseSchema, ReviewUpdateSchema

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _to_response(review: Review) -> ReviewResponseSchema:
    return ReviewResponseSchema(
        id=UUID(str(review.id)),
        user_id=UUID(str(review.client_id)),
        client_id=UUID(str(review.client_id)),
        provider_id=UUID(str(review.provider_id)),
        service_id=UUID(str(review.service_id)),
        rating=review.rating,
        comment=review.comment,
        guest_name=review.guest_name,
        guest_email=review.guest_email,
        status=review.status,
        moderated_by=UUID(str(review.moderated_by)) if review.moderated_by else None,
        moderation_notes=review.moderation_notes,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.post("/", response_model=ReviewResponseSchema, status_code=201)
async def create_review(
    payload: ReviewCreateSchema,
    use_case: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponseSchema:
    """
    Create a new review.
    """
    command = CreatePublicReviewCommand(
        client_id=str(payload.client_id) if payload.client_id else None,
        provider_id=str(payload.provider_id),
        service_id=str(payload.service_id),
        rating=payload.rating,
        comment=payload.comment,
        guest_name=payload.guest_name,
        guest_email=str(payload.guest_email) if payload.guest_email else None,
    )
    try:
        review = await use_case.create_public_review(command)
        return _to_response(review)
    except ReviewValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{review_id}", response_model=ReviewResponseSchema)
async def get_review(
    review_id: UUID,
    use_case: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponseSchema:
    """Get review by ID."""
    review = await use_case.get_review(ReviewId(str(review_id)))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return _to_response(review)


@router.get("/", response_model=list[ReviewResponseSchema])
async def list_reviews(
    service_id: UUID = Query(..., description="Service ID to filter reviews"),
    use_case: ReviewUseCases = Depends(get_review_use_cases),
) -> list[ReviewResponseSchema]:
    """List reviews for a service."""
    reviews = await use_case.list_reviews_for_service(ServiceId(str(service_id)))
    return [_to_response(review) for review in reviews]


@router.put("/{review_id}", response_model=ReviewResponseSchema)
async def update_review(
    review_id: UUID,
    payload: ReviewUpdateSchema,
    use_case: ReviewUseCases = Depends(get_review_use_cases),
) -> ReviewResponseSchema:
    """Update a review."""
    request = UpdateReviewRequest(
        review_id=ReviewId(str(review_id)),
        rating=payload.rating,
        comment=payload.comment,
    )
    try:
        review = await use_case.update_review(request)
        return _to_response(review)
    except ReviewNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ReviewValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    use_case: ReviewUseCases = Depends(get_review_use_cases),
) -> None:
    """Delete a review."""
    try:
        await use_case.delete_review(ReviewId(str(review_id)))
    except ReviewNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mano.application.dtos.availability_dtos import CreateAvailabilityRequest, UpdateAvailabilityRequest
from mano.application.use_cases.availability_use_cases import AvailabilityUseCases
from mano.dependencies import get_availability_use_cases, get_current_user
from mano.domain.exceptions.base import AvailabilityNotFoundError, DomainError
from mano.domain.models.service_model import ProviderId
from mano.domain.models.user import UserProfile
from mano.presentation.schemas.availability_schemas import (
    AvailabilityResponseSchema,
    CreateAvailabilitySchema,
    UpdateAvailabilitySchema,
)
from mano.utils.pagination import PaginatedResponse, Pagination, PaginationParams


router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/", response_model=AvailabilityResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_availability(
    payload: CreateAvailabilitySchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: AvailabilityUseCases = Depends(get_availability_use_cases),
) -> AvailabilityResponseSchema:
    """Create a new availability slot."""
    try:
        request = CreateAvailabilityRequest(
            provider_id=ProviderId(str(payload.provider_id)),
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_available=payload.is_available,
            specific_date=payload.specific_date,
        )
        created = await use_case.create_availability(request)
        return AvailabilityResponseSchema(
            id=UUID(str(created.id)),
            provider_id=UUID(str(created.provider_id)),
            day_of_week=created.day_of_week,
            start_time=created.start_time,
            end_time=created.end_time,
            is_available=created.is_available,
            specific_date=created.specific_date,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{availability_id}", response_model=AvailabilityResponseSchema)
async def get_availability(
    availability_id: str,
    use_case: AvailabilityUseCases = Depends(get_availability_use_cases),
) -> AvailabilityResponseSchema:
    """Get availability by ID."""
    try:
        availability = await use_case.get_availability_by_id(availability_id)
        return AvailabilityResponseSchema(
            id=UUID(str(availability.id)),
            provider_id=UUID(str(availability.provider_id)),
            day_of_week=availability.day_of_week,
            start_time=availability.start_time,
            end_time=availability.end_time,
            is_available=availability.is_available,
            specific_date=availability.specific_date,
            created_at=availability.created_at,
            updated_at=availability.updated_at,
        )
    except AvailabilityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{availability_id}", response_model=AvailabilityResponseSchema)
async def update_availability(
    availability_id: str,
    payload: UpdateAvailabilitySchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: AvailabilityUseCases = Depends(get_availability_use_cases),
) -> AvailabilityResponseSchema:
    """Update an availability slot."""
    try:
        request = UpdateAvailabilityRequest(
            day_of_week=payload.day_of_week,
            start_time=payload.start_time,
            end_time=payload.end_time,
            is_available=payload.is_available,
            specific_date=payload.specific_date,
        )
        updated = await use_case.update_availability(availability_id, request)
        return AvailabilityResponseSchema(
            id=UUID(str(updated.id)),
            provider_id=UUID(str(updated.provider_id)),
            day_of_week=updated.day_of_week,
            start_time=updated.start_time,
            end_time=updated.end_time,
            is_available=updated.is_available,
            specific_date=updated.specific_date,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
    except AvailabilityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability(
    availability_id: str,
    current_user: UserProfile = Depends(get_current_user),
    use_case: AvailabilityUseCases = Depends(get_availability_use_cases),
) -> None:
    """Delete an availability slot."""
    try:
        await use_case.delete_availability(availability_id)
    except AvailabilityNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Availability not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PaginatedResponse[AvailabilityResponseSchema])
async def list_availability(
    params: PaginationParams = Depends(PaginationParams.from_query),
    provider_id: UUID | None = Query(None, description="Filter by provider ID"),
    use_case: AvailabilityUseCases = Depends(get_availability_use_cases),
) -> PaginatedResponse[AvailabilityResponseSchema]:
    """List availability slots with optional provider filter."""
    try:
        if provider_id:
            slots = await use_case.list_by_provider(str(provider_id))
        else:
            slots = await use_case.list_all()
        schemas = [
            AvailabilityResponseSchema(
                id=UUID(str(dto.id)),
                provider_id=UUID(str(dto.provider_id)),
                day_of_week=dto.day_of_week,
                start_time=dto.start_time,
                end_time=dto.end_time,
                is_available=dto.is_available,
                specific_date=dto.specific_date,
                created_at=dto.created_at,
                updated_at=dto.updated_at,
            )
            for dto in slots
        ]
        return Pagination.paginate_items(schemas, params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

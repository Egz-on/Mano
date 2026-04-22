from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from mano.dependencies import get_current_user, get_service_use_cases
from mano.domain.models.user import UserProfile
from mano.domain.models.service_model import ProviderId, CategoryId, Service, ServiceId
from mano.application.use_cases.service_use_cases import ServiceUseCases
from mano.application.dtos.service_dtos import CreateServiceRequest, UpdateServiceRequest
from mano.presentation.schemas.service_schemas import (
    CreateServiceSchema,
    ServiceResponseSchema,
    UpdateServiceSchema,
)
from mano.domain.exceptions.base import DomainError, ServiceNotFoundError, ServiceAlreadyExistsError
from mano.utils.pagination import Pagination, PaginationParams, PaginatedResponse

router = APIRouter(prefix="/services", tags=["services"])


def _ensure_can_create_service(*, current_user: UserProfile, provider_id: ProviderId, is_featured: bool) -> None:
    if current_user.is_admin():
        return
    if not current_user.is_provider():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can create services")
    if str(current_user.id) != str(provider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot create services for another provider")
    if is_featured:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can feature services")


def _ensure_can_manage_service(
    *, current_user: UserProfile, service: Service, requested_featured: bool | None = None
) -> None:
    if current_user.is_admin():
        return
    if not current_user.is_provider():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only providers can manage services")
    if str(current_user.id) != str(service.provider_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot manage another provider's service")
    if requested_featured:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can feature services")


@router.post("/", response_model=ServiceResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: CreateServiceSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: ServiceUseCases = Depends(get_service_use_cases),
) -> ServiceResponseSchema:
    """Create a new service."""
    try:
        provider_id = ProviderId(str(payload.provider_id))
        _ensure_can_create_service(
            current_user=current_user,
            provider_id=provider_id,
            is_featured=payload.is_featured,
        )

        request = CreateServiceRequest(
            provider_id=provider_id,
            category_id=CategoryId(str(payload.category_id)),
            title=payload.title,
            description=payload.description,
            price=payload.price,
            currency=payload.currency,
            pricing_type=payload.pricing_type,
            service_areas=payload.service_areas,
            service_metadata=payload.service_metadata,
            images=payload.images,
            is_active=payload.is_active,
            is_featured=payload.is_featured,
        )

        service = await use_case.create_service(request)
        return ServiceResponseSchema.model_validate(service.to_dict())

    except ServiceAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{service_id}", response_model=ServiceResponseSchema)
async def get_service(
    service_id: str,
    use_case: ServiceUseCases = Depends(get_service_use_cases),
) -> ServiceResponseSchema:
    """Get service by ID."""
    try:
        service = await use_case.get_service_by_id(ServiceId(service_id))
        return ServiceResponseSchema.model_validate(service.to_dict())
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{service_id}", response_model=ServiceResponseSchema)
async def update_service(
    service_id: str,
    payload: UpdateServiceSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: ServiceUseCases = Depends(get_service_use_cases),
) -> ServiceResponseSchema:
    """Update an existing service."""
    try:
        existing_service = await use_case.get_service_by_id(ServiceId(service_id))
        _ensure_can_manage_service(
            current_user=current_user,
            service=existing_service,
            requested_featured=payload.is_featured,
        )

        request = UpdateServiceRequest(
            title=payload.title,
            description=payload.description,
            price=payload.price,
            currency=payload.currency,
            pricing_type=payload.pricing_type,
            service_areas=payload.service_areas,
            service_metadata=payload.service_metadata,
            images=payload.images,
            is_active=payload.is_active,
            is_featured=payload.is_featured,
        )

        updated_service = await use_case.update_service(service_id, request)
        return ServiceResponseSchema.model_validate(updated_service.to_dict())

    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: str,
    current_user: UserProfile = Depends(get_current_user),
    use_case: ServiceUseCases = Depends(get_service_use_cases),
) -> None:
    """Delete a service."""
    try:
        existing_service = await use_case.get_service_by_id(ServiceId(service_id))
        _ensure_can_manage_service(current_user=current_user, service=existing_service)
        await use_case.delete_service(ServiceId(service_id))
    except ServiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PaginatedResponse[ServiceResponseSchema])
async def list_services(
    params: PaginationParams = Depends(PaginationParams.from_query),
    use_case: ServiceUseCases = Depends(get_service_use_cases),
) -> PaginatedResponse[ServiceResponseSchema]:
    """List services with pagination."""
    try:
        # Note: use_case.list_services() currently returns all services.
        # Ideally, we should pass pagination params down to the repository.
        # implementing in-memory pagination for now as per current use_case signature

        services_dtos = await use_case.list_services()

        # Convert DTOs to Schemas is handled by model_validate but here we have DTOs
        # ServiceResponseDTO has model_config from_attributes, so it acts like a Pydantic model compatible object

        # We need to map DTOs to Pydantic Schemas to be safe
        services_schemas = [
            ServiceResponseSchema(
                id=UUID(str(dto.id)),
                provider_id=UUID(str(dto.provider_id)),
                category_id=UUID(str(dto.category_id)),
                title=dto.title,
                description=dto.description,
                price=dto.price,
                currency=dto.currency,
                pricing_type=dto.pricing_type,
                service_areas=dto.service_areas,
                service_metadata=dto.service_metadata,
                images=dto.images,
                rating=dto.rating,
                review_count=dto.review_count,
                is_active=dto.is_active,
                is_featured=dto.is_featured,
                created_at=dto.created_at,
                updated_at=dto.updated_at,
            )
            for dto in services_dtos
        ]

        return Pagination.paginate_items(services_schemas, params)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

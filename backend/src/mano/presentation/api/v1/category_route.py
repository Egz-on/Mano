from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from mano.application.dtos.category_dtos import CreateCategoryRequest, UpdateCategoryRequest
from mano.application.use_cases.category_use_cases import CategoryUseCases
from mano.dependencies import get_category_use_cases, get_current_user
from mano.domain.exceptions.base import CategoryAlreadyExistsError, CategoryNotFoundError, DomainError
from mano.domain.models.category import CategoryId
from mano.domain.models.user import UserProfile
from mano.presentation.schemas.category_schemas import (
    CategoryResponseSchema,
    CreateCategorySchema,
    UpdateCategorySchema,
)
from mano.utils.pagination import PaginatedResponse, Pagination, PaginationParams


router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/", response_model=CategoryResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CreateCategorySchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponseSchema:
    """Create a new category."""
    try:
        request = CreateCategoryRequest(
            name=payload.name,
            slug=payload.slug,
            icon=payload.icon,
            description=payload.description,
            parent_id=CategoryId(str(payload.parent_id)) if payload.parent_id else None,
            is_active=payload.is_active,
            display_order=payload.display_order,
        )
        created = await use_case.create_category(request)
        return CategoryResponseSchema(
            id=UUID(str(created.id)),
            name=created.name,
            slug=created.slug,
            icon=created.icon,
            description=created.description,
            parent_id=UUID(str(created.parent_id)) if created.parent_id else None,
            is_active=created.is_active,
            display_order=created.display_order,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
    except CategoryAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponseSchema)
async def get_category(
    category_id: str,
    use_case: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponseSchema:
    """Get category by ID."""
    try:
        category = await use_case.get_category_by_id(category_id)
        return CategoryResponseSchema(
            id=UUID(str(category.id)),
            name=category.name,
            slug=category.slug,
            icon=category.icon,
            description=category.description,
            parent_id=UUID(str(category.parent_id)) if category.parent_id else None,
            is_active=category.is_active,
            display_order=category.display_order,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponseSchema)
async def update_category(
    category_id: str,
    payload: UpdateCategorySchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: CategoryUseCases = Depends(get_category_use_cases),
) -> CategoryResponseSchema:
    """Update an existing category."""
    try:
        request = UpdateCategoryRequest(
            name=payload.name,
            slug=payload.slug,
            icon=payload.icon,
            description=payload.description,
            parent_id=CategoryId(str(payload.parent_id)) if payload.parent_id else None,
            is_active=payload.is_active,
            display_order=payload.display_order,
        )
        updated = await use_case.update_category(category_id, request)
        return CategoryResponseSchema(
            id=UUID(str(updated.id)),
            name=updated.name,
            slug=updated.slug,
            icon=updated.icon,
            description=updated.description,
            parent_id=UUID(str(updated.parent_id)) if updated.parent_id else None,
            is_active=updated.is_active,
            display_order=updated.display_order,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user: UserProfile = Depends(get_current_user),
    use_case: CategoryUseCases = Depends(get_category_use_cases),
) -> None:
    """Delete a category."""
    try:
        await use_case.delete_category(category_id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PaginatedResponse[CategoryResponseSchema])
async def list_categories(
    params: PaginationParams = Depends(PaginationParams.from_query),
    use_case: CategoryUseCases = Depends(get_category_use_cases),
) -> PaginatedResponse[CategoryResponseSchema]:
    """List categories with pagination."""
    try:
        categories_dtos = await use_case.list_categories()
        categories_schemas = [
            CategoryResponseSchema(
                id=UUID(str(dto.id)),
                name=dto.name,
                slug=dto.slug,
                icon=dto.icon,
                description=dto.description,
                parent_id=UUID(str(dto.parent_id)) if dto.parent_id else None,
                is_active=dto.is_active,
                display_order=dto.display_order,
                created_at=dto.created_at,
                updated_at=dto.updated_at,
            )
            for dto in categories_dtos
        ]
        return Pagination.paginate_items(categories_schemas, params)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

from fastapi import APIRouter, Depends, HTTPException, status
from workmate.dependencies import get_current_user, get_user_use_cases
from workmate.domain.models.user import UserProfile
from workmate.presentation.schemas.user_schemas import UserProfileResponse, UserProfileUpdateRequest
from workmate.application.use_cases.user_use_cases import UserUseCases
from workmate.application.dtos.user_dtos import UpdateUserRequest
from workmate.domain.exceptions.base import UserNotFoundError, DomainError
from workmate.utils.pagination import Pagination, PaginationParams, PaginatedResponse
from workmate.dependencies import strict_auth_limiter
from fastapi import Request

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=PaginatedResponse[UserProfileResponse], summary="List users")
async def list_users(
    params: PaginationParams = Depends(PaginationParams.from_query),
    use_case: UserUseCases = Depends(get_user_use_cases),
    current_user: UserProfile = Depends(get_current_user),
) -> PaginatedResponse[UserProfileResponse]:
    """List users with pagination."""

    try:
        if not current_user.is_admin():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        result = await use_case.list_users()
        users = result
        if params.sort and users:
            sort_field = params.sort
            if hasattr(users[0], sort_field):
                reverse = params.order == "desc"
                users = sorted(users, key=lambda u: getattr(u, sort_field), reverse=reverse)

        user_responses = [
            UserProfileResponse(
                id=user.id,
                auth_user_id=user.auth_user_id,
                full_name=user.full_name,
                phone=user.phone,
                avatar_url=user.avatar_url,
                bio=user.bio,
                role=user.role,
                city=user.city,
                address=user.address,
                years_of_experience=user.years_of_experience,
                company_name=user.company_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
            )
            for user in users
        ]
        return Pagination.paginate_items(user_responses, params)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserProfileResponse, summary="my profile")
async def get_my_profile(current_user: UserProfile = Depends(get_current_user)) -> UserProfileResponse:
    """Get current user's profile."""
    from uuid import UUID

    return UserProfileResponse(
        id=UUID(current_user.id.value),
        auth_user_id=UUID(current_user.auth_user_id.value),
        full_name=current_user.full_name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        role=current_user.role,
        city=current_user.city,
        address=current_user.address,
        years_of_experience=current_user.years_of_experience,
        company_name=current_user.company_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login,
    )


@router.get("/{user_id}", response_model=UserProfileResponse, summary="Get user by ID")
async def get_user(user_id: str, use_case: UserUseCases = Depends(get_user_use_cases)) -> UserProfileResponse:
    """Get user by ID."""
    try:
        result = await use_case.get_user(user_id)

        return UserProfileResponse(
            id=result.id,
            auth_user_id=result.auth_user_id,
            full_name=result.full_name,
            phone=result.phone,
            avatar_url=result.avatar_url,
            bio=result.bio,
            role=result.role,
            city=result.city,
            address=result.address,
            years_of_experience=result.years_of_experience,
            company_name=result.company_name,
            created_at=result.created_at,
            updated_at=result.updated_at,
            last_login=result.last_login,
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@strict_auth_limiter
@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    request: Request,
    payload: UserProfileUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserProfileResponse:
    """Users update their own profile."""
    dto = UpdateUserRequest(**payload.model_dump(exclude_unset=True))
    updated = await use_cases.update_user_profile(current_user.id.value, dto, current_user)
    return UserProfileResponse(
        id=updated.id,
        auth_user_id=updated.auth_user_id,
        full_name=updated.full_name,
        phone=updated.phone,
        avatar_url=updated.avatar_url,
        bio=updated.bio,
        role=updated.role,
        city=updated.city,
        address=updated.address,
        years_of_experience=updated.years_of_experience,
        company_name=updated.company_name,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        last_login=updated.last_login,
    )


@strict_auth_limiter
@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_by_id(
    request: Request,
    user_id: str,
    payload: UserProfileUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserProfileResponse:
    """Admins update any user (including role, status)."""
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admin access required")

    dto = UpdateUserRequest(**payload.model_dump(exclude_unset=True))
    updated = await use_cases.update_user_profile(user_id, dto, current_user)
    return UserProfileResponse(
        id=updated.id,
        auth_user_id=updated.auth_user_id,
        full_name=updated.full_name,
        phone=updated.phone,
        avatar_url=updated.avatar_url,
        bio=updated.bio,
        role=updated.role,
        city=updated.city,
        address=updated.address,
        years_of_experience=updated.years_of_experience,
        company_name=updated.company_name,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        last_login=updated.last_login,
    )

from fastapi import APIRouter, Depends, HTTPException, status
from mano.dependencies import get_current_user, get_user_use_cases
from mano.domain.models.user import UserProfile
from mano.presentation.schemas.user_schemas import UserProfileResponse, UserProfileUpdateRequest
from mano.application.use_cases.user_use_cases import UserUseCases
from mano.application.dtos.user_dtos import UpdateUserRequest
from mano.domain.exceptions.base import UserNotFoundError, DomainError
from mano.utils.pagination import Pagination, PaginationParams, PaginatedResponse
from mano.dependencies import strict_auth_limiter
from fastapi import Request
from uuid import UUID

router = APIRouter(prefix="/users", tags=["users"])


def _to_profile_response(user: UserProfile | object) -> UserProfileResponse:
    return UserProfileResponse(
        id=UUID(getattr(user.id, "value", str(user.id))),
        auth_user_id=UUID(getattr(user.auth_user_id, "value", str(user.auth_user_id))),
        name=user.name,
        surname=user.surname,
        phone=user.phone,
        avatar_url=user.avatar_url,
        bio=user.bio,
        role=user.role,
        city=user.city,
        address=user.address,
        years_of_experience=user.years_of_experience,
        company_name=user.company_name,
        is_active=user.is_active,
        is_online=user.is_online,
        approval_status=user.approval_status,
        latitude=user.latitude,
        longitude=user.longitude,
        fcm_token=user.fcm_token,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login,
    )


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

        user_responses = [_to_profile_response(user) for user in users]
        return Pagination.paginate_items(user_responses, params)
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserProfileResponse, summary="my profile")
async def get_my_profile(current_user: UserProfile = Depends(get_current_user)) -> UserProfileResponse:
    """Get current user's profile."""
    return _to_profile_response(current_user)


@router.get("/{user_id}", response_model=UserProfileResponse, summary="Get user by ID")
async def get_user(user_id: str, use_case: UserUseCases = Depends(get_user_use_cases)) -> UserProfileResponse:
    """Get user by ID."""
    try:
        result = await use_case.get_user(user_id)

        return _to_profile_response(result)
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
    return _to_profile_response(updated)


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
    return _to_profile_response(updated)

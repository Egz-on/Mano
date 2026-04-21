"""User use cases."""

from __future__ import annotations

from datetime import UTC, datetime

from mano.application.dtos.user_dtos import CreateUserRequest, UpdateUserRequest, UserResponse
from mano.common.uuid_utils import uuid_to_str
from mano.domain.exceptions.base import DomainError
from mano.domain.models.user import PhoneNumber, UserAuthId, UserId, UserProfile
from mano.domain.services.user_service import UserService


class UserUseCases:
    """User use cases for handling user-related business operations."""

    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    async def create_user(self, request: CreateUserRequest) -> UserResponse:
        try:
            phone = PhoneNumber(request.phone)
        except ValueError as exc:
            raise DomainError(f"Invalid phone number: {exc}") from exc

        now = datetime.now(UTC)
        new_user = UserProfile(
            id=UserId(),
            auth_user_id=UserAuthId(value=uuid_to_str(request.auth_user_id)),
            full_name=request.full_name,
            phone=str(phone),
            avatar_url=request.avatar_url,
            bio=request.bio,
            role=request.role,
            city=request.city,
            address=request.address,
            years_of_experience=request.years_of_experience,
            company_name=request.company_name,
            profile_metadata=request.profile_metadata or {},
            created_at=now,
            updated_at=now,
            last_login=now,
        )

        created_user = await self.user_service.create_user_profile(new_user)
        return UserResponse.from_domain(created_user)

    async def get_user(self, user_id: str) -> UserResponse:
        user = await self.user_service.get_user_by_id(UserId(user_id))
        return UserResponse.from_domain(user)

    async def update_user_profile(
        self, user_id: str, request: UpdateUserRequest, current_user: UserProfile
    ) -> UserResponse:
        user = await self.user_service.get_user_by_id(UserId(user_id))

        if request.role is not None and not current_user.is_admin():
            raise DomainError("Only admin can change roles")
        if not current_user.is_admin() and str(current_user.id) != user_id:
            raise DomainError("Can only update your own profile")

        updated_user = user.update_profile(
            full_name=request.full_name,
            phone=request.phone,
            avatar_url=request.avatar_url,
            bio=request.bio,
            city=request.city,
            address=request.address,
            years_of_experience=request.years_of_experience,
            company_name=request.company_name,
        )
        if request.role is not None:
            updated_user = UserProfile(
                **{**updated_user.__dict__, "role": request.role, "updated_at": datetime.now(UTC)}
            )
        if request.profile_metadata is not None:
            updated_user = UserProfile(
                **{
                    **updated_user.__dict__,
                    "profile_metadata": request.profile_metadata,
                    "updated_at": datetime.now(UTC),
                }
            )

        saved = await self.user_service.update_user_profile(updated_user)
        return UserResponse.from_domain(saved)

    async def delete_user(self, user_id: str) -> None:
        await self.user_service.delete_user(UserId(user_id))

    async def list_users(self) -> list[UserResponse]:
        users = await self.user_service.list_users()
        return [UserResponse.from_domain(user) for user in users]

    async def recalculate_user_stats(self, auth_user_id: str) -> UserResponse:
        updated_user = await self.user_service.recalculate_user_stats(UserAuthId(auth_user_id))
        return UserResponse.from_domain(updated_user)

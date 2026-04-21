"""SQLAlchemy implementation of the user repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from workmate.common.uuid_utils import uuid_to_str
from workmate.domain.models.user import UserAuthId, UserId, UserProfile, UserRole
from workmate.domain.repositories.user_repository import UserRepository
from workmate.infrastructure.database.models import ReviewModel, ServiceModel, UserProfileModel


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of the user repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_domain(model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=UserId(str(model.id)),
            auth_user_id=UserAuthId(str(model.auth_user_id)),
            full_name=cast(str, model.full_name),
            phone=cast(str, model.phone),
            avatar_url=cast(str | None, model.avatar_url),
            bio=cast(str | None, model.bio),
            role=UserRole(cast(str, model.role)),
            city=cast(str | None, model.city),
            address=cast(str | None, model.address),
            years_of_experience=cast(int | None, model.years_of_experience),
            company_name=cast(str | None, model.company_name),
            profile_metadata=cast(dict[str, Any], model.profile_metadata or {}),
            created_at=cast(datetime, model.created_at),
            updated_at=cast(datetime, model.updated_at),
            last_login=cast(datetime | None, model.last_login),
        )

    @staticmethod
    def _apply_domain_to_model(domain: UserProfile, model: UserProfileModel) -> None:
        model.auth_user_id = uuid_to_str(domain.auth_user_id)
        model.full_name = domain.full_name
        model.phone = domain.phone
        model.avatar_url = domain.avatar_url
        model.bio = domain.bio
        model.role = str(domain.role)
        model.city = domain.city
        model.address = domain.address
        model.years_of_experience = domain.years_of_experience
        model.company_name = domain.company_name
        model.profile_metadata = domain.profile_metadata
        model.updated_at = domain.updated_at
        model.last_login = domain.last_login

    async def create_user_profile(self, user: UserProfile) -> UserProfile:
        model = UserProfileModel(
            id=uuid_to_str(user.id),
            auth_user_id=uuid_to_str(user.auth_user_id),
            full_name=user.full_name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            role=str(user.role),
            city=user.city,
            address=user.address,
            years_of_experience=user.years_of_experience,
            company_name=user.company_name,
            profile_metadata=user.profile_metadata or {},
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def get_user_by_id(self, user_id: UserId) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.id == uuid_to_str(user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_user_by_auth_user_id(self, auth_user_id: UserAuthId) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.auth_user_id == uuid_to_str(auth_user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_user(self, user: UserProfile) -> UserProfile:
        stmt = select(UserProfileModel).where(UserProfileModel.id == uuid_to_str(user.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"User with ID {user.id} not found.")

        self._apply_domain_to_model(user, model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_domain(model)

    async def delete_user(self, user_id: UserId) -> None:
        stmt = delete(UserProfileModel).where(UserProfileModel.id == uuid_to_str(user_id))
        await self._session.execute(stmt)

    async def list_users(self) -> list[UserProfile]:
        stmt = select(UserProfileModel)
        result = await self._session.execute(stmt)
        return [self._to_domain(model) for model in result.scalars().all()]

    async def get_user_stats(self, user_id: UserId) -> dict[str, Any]:
        service_count = await self._session.scalar(
            select(func.count(ServiceModel.id)).where(ServiceModel.provider_id == uuid_to_str(user_id))
        )
        review_stats = await self._session.execute(
            select(func.avg(ReviewModel.rating).label("avg_rating"), func.count(ReviewModel.id).label("review_count"))
            .where(ReviewModel.provider_id == uuid_to_str(user_id))
            .where(ReviewModel.status == "approved")
        )

        avg_rating, review_count = review_stats.first() or (None, 0)
        return {
            "total_services": service_count or 0,
            "average_rating": float(avg_rating or 0.0),
            "total_reviews": review_count or 0,
        }

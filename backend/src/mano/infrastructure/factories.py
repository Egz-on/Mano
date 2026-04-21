"""Infrastructure factory helpers."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from mano.domain.repositories.auth_repository import AuthRepository
from mano.domain.repositories.availability_repository import AvailabilityRepository
from mano.domain.repositories.category_repository import CategoryRepository
from mano.domain.repositories.image_storage_port import IImageStoragePort
from mano.domain.repositories.review_repository import ReviewRepository
from mano.domain.repositories.service_repository import ServiceRepository
from mano.domain.repositories.user_repository import UserRepository
from mano.domain.services.availability_service import AvailabilityService
from mano.domain.services.category_service import CategoryService
from mano.domain.services.rating_service import RatingService
from mano.domain.services.review_service import ReviewService
from mano.domain.services.service_services import ServiceService
from mano.domain.services.user_service import UserService
from mano.infrastructure.repositories.sqlalchemy_auth_repository import SQLAlchemyAuthRepository
from mano.infrastructure.repositories.sqlalchemy_availability_repository import SQLAlchemyAvailabilityRepository
from mano.infrastructure.repositories.sqlalchemy_category_repository import SQLAlchemyCategoryRepository
from mano.infrastructure.repositories.sqlalchemy_review_repository import SQLAlchemyReviewRepository
from mano.infrastructure.repositories.sqlalchemy_service_repository import SQLAlchemyServiceRepository
from mano.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


class InfrastructureServiceFactory:
    """Concrete implementation of repository and service factories."""

    @staticmethod
    def create_user_repository(session: AsyncSession) -> UserRepository:
        return SQLAlchemyUserRepository(session)

    @staticmethod
    def create_auth_repository(session: AsyncSession) -> AuthRepository:
        return SQLAlchemyAuthRepository(session)

    @staticmethod
    def create_service_repository(session: AsyncSession) -> ServiceRepository:
        return SQLAlchemyServiceRepository(session)

    @staticmethod
    def create_review_repository(session: AsyncSession) -> ReviewRepository:
        return SQLAlchemyReviewRepository(session)

    @staticmethod
    def create_category_repository(session: AsyncSession) -> CategoryRepository:
        return SQLAlchemyCategoryRepository(session)

    @staticmethod
    def create_availability_repository(session: AsyncSession) -> AvailabilityRepository:
        return SQLAlchemyAvailabilityRepository(session)

    @staticmethod
    def create_user_service(user_repository: UserRepository, cache: object | None = None) -> UserService:
        return UserService(user_repository, cache=cache)

    @staticmethod
    def create_service_service(
        service_repository: ServiceRepository,
        image_storage: IImageStoragePort,
    ) -> ServiceService:
        return ServiceService(service_repository, image_storage)

    @staticmethod
    def create_review_service(review_repository: ReviewRepository) -> ReviewService:
        return ReviewService(review_repository)

    @staticmethod
    def create_category_service(category_repository: CategoryRepository) -> CategoryService:
        return CategoryService(category_repository)

    @staticmethod
    def create_availability_service(availability_repository: AvailabilityRepository) -> AvailabilityService:
        return AvailabilityService(availability_repository)

    @staticmethod
    def create_rating_service(
        review_repository: ReviewRepository,
        service_repository: ServiceRepository,
    ) -> RatingService:
        return RatingService(review_repository, service_repository)

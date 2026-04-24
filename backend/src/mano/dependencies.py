"""Application dependency wiring."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from collections.abc import Callable
from uuid import NAMESPACE_DNS, uuid5

import redis.asyncio as redis
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mano.application.use_cases.auth_use_cases import AuthUseCases
from mano.application.use_cases.availability_use_cases import AvailabilityUseCases
from mano.application.use_cases.category_use_cases import CategoryUseCases
from mano.application.use_cases.chat_use_cases import ChatUseCases
from mano.application.use_cases.job_use_cases import JobUseCases
from mano.application.use_cases.review_use_cases import ReviewUseCases
from mano.application.use_cases.service_use_cases import ServiceUseCases
from mano.application.use_cases.user_use_cases import UserUseCases
from mano.domain.models.user import PhoneNumber, UserAuthId, UserId, UserProfile, UserRole
from mano.domain.repositories.auth_repository import AuthRepository
from mano.domain.repositories.email_sender_port import EmailSenderPort
from mano.domain.repositories.image_storage_port import IImageStoragePort
from mano.domain.services.auth_service import AuthService
from mano.domain.services.availability_service import AvailabilityService
from mano.domain.services.category_service import CategoryService
from mano.domain.services.chat_service import ChatService
from mano.domain.services.job_service import JobService
from mano.domain.services.rating_service import RatingService
from mano.domain.services.review_service import ReviewService
from mano.domain.services.service_services import ServiceService
from mano.domain.services.user_service import UserService
from mano.infrastructure.cache.connection import get_redis_client
from mano.infrastructure.config.settings import Settings, get_settings
from mano.infrastructure.database.connection import get_db_session
from mano.infrastructure.external.smtp_email_sender import SMTPEmailSender
from mano.infrastructure.factories import InfrastructureServiceFactory
from mano.infrastructure.repositories.cloudinary_storage import CloudinaryStorageAdapter
from mano.infrastructure.security.local_auth import (
    DEMO_USERS,
    authenticate_user,
    create_access_token,
    decode_access_token,
)
from mano.infrastructure.security.password_hasher import BcryptPasswordHasher
from mano.infrastructure.security.rate_limiter import (
    lenient_auth_limiter,
    moderate_auth_limiter,
    setup_rate_limiting,
    strict_auth_limiter,
)

__all__ = [
    "get_db_session",
    "get_redis_client",
    "get_settings",
    "get_auth_repository",
    "get_auth_service",
    "get_auth_use_cases",
    "get_access_token_factory",
    "get_is_development",
    "authenticate_demo_credentials",
    "get_email_sender",
    "get_user_service",
    "get_service_service",
    "get_category_service",
    "get_availability_service",
    "get_review_service",
    "get_rating_service",
    "get_chat_service",
    "get_job_service",
    "get_user_use_cases",
    "get_service_use_cases",
    "get_category_use_cases",
    "get_availability_use_cases",
    "get_review_use_cases",
    "get_chat_use_cases",
    "get_job_use_cases",
    "get_current_user",
    "resolve_user_from_token",
    "setup_rate_limiting",
    "strict_auth_limiter",
    "moderate_auth_limiter",
    "lenient_auth_limiter",
    "get_image_storage",
    "ImageStorageDep",
]

AccessTokenFactory = Callable[[str, str, str, str], str]


def _derive_auth_user_id(email: str) -> UserAuthId:
    return UserAuthId(str(uuid5(NAMESPACE_DNS, f"mano:{email.strip().lower()}")))


async def get_auth_repository(session: AsyncSession = Depends(get_db_session)) -> AuthRepository:
    factory = InfrastructureServiceFactory()
    return factory.create_auth_repository(session)


async def get_user_service(
    session: AsyncSession = Depends(get_db_session),
    redis_client: redis.Redis = Depends(get_redis_client),
) -> UserService:
    factory = InfrastructureServiceFactory()
    user_repository = factory.create_user_repository(session)
    return factory.create_user_service(user_repository, cache=redis_client)


async def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository),
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(auth_repository, user_service, BcryptPasswordHasher())


def get_email_sender(settings: Settings = Depends(get_settings)) -> EmailSenderPort:
    return SMTPEmailSender(
        host=settings.smtp.host,
        port=settings.smtp.port,
        sender_email=settings.smtp.sender_email,
        sender_name=settings.smtp.sender_name,
        username=settings.smtp.user,
        password=settings.smtp.password,
        use_tls=settings.smtp.use_tls,
        use_starttls=settings.smtp.use_starttls,
        timeout=settings.smtp.timeout_seconds,
    )


async def get_service_service(session: AsyncSession = Depends(get_db_session)) -> ServiceService:
    factory = InfrastructureServiceFactory()
    image_storage = get_image_storage()
    service_repository = factory.create_service_repository(session)
    return factory.create_service_service(service_repository, image_storage)


async def get_category_service(session: AsyncSession = Depends(get_db_session)) -> CategoryService:
    factory = InfrastructureServiceFactory()
    category_repository = factory.create_category_repository(session)
    return factory.create_category_service(category_repository)


async def get_availability_service(session: AsyncSession = Depends(get_db_session)) -> AvailabilityService:
    factory = InfrastructureServiceFactory()
    availability_repository = factory.create_availability_repository(session)
    return factory.create_availability_service(availability_repository)


async def get_review_service(session: AsyncSession = Depends(get_db_session)) -> ReviewService:
    factory = InfrastructureServiceFactory()
    review_repository = factory.create_review_repository(session)
    return factory.create_review_service(review_repository)


async def get_rating_service(session: AsyncSession = Depends(get_db_session)) -> RatingService:
    factory = InfrastructureServiceFactory()
    review_repository = factory.create_review_repository(session)
    service_repository = factory.create_service_repository(session)
    return factory.create_rating_service(review_repository, service_repository)


async def get_chat_service(session: AsyncSession = Depends(get_db_session)) -> ChatService:
    factory = InfrastructureServiceFactory()
    chat_repository = factory.create_chat_repository(session)
    return factory.create_chat_service(chat_repository)


async def get_job_service(session: AsyncSession = Depends(get_db_session)) -> JobService:
    factory = InfrastructureServiceFactory()
    job_repository = factory.create_job_repository(session)
    return factory.create_job_service(job_repository)


async def get_auth_use_cases(
    auth_service: AuthService = Depends(get_auth_service),
    email_sender: EmailSenderPort = Depends(get_email_sender),
    settings: Settings = Depends(get_settings),
) -> AuthUseCases:
    return AuthUseCases(auth_service, email_sender, settings.frontend_url)


def authenticate_demo_credentials(email: str, password: str) -> tuple[str, str, str, str] | None:
    """Validate local demo credentials and return auth-ready claims."""
    demo_user = authenticate_user(email, password)
    if demo_user is None:
        return None
    return demo_user["email"], demo_user["name"], demo_user["surname"], demo_user["role"]


def get_access_token_factory(settings: Settings = Depends(get_settings)) -> AccessTokenFactory:
    """Return a helper that issues local access tokens using current settings."""

    def create_token(subject: str, role: str, name: str, surname: str) -> str:
        return create_access_token(
            secret_key=settings.secret_key or "dev-secret-change-me",
            subject=subject,
            role=role,
            name=name,
            surname=surname,
        )

    return create_token


def get_is_development(settings: Settings = Depends(get_settings)) -> bool:
    """Expose the current development-mode flag to the web layer."""
    return settings.is_development


async def get_user_use_cases(user_service: UserService = Depends(get_user_service)) -> UserUseCases:
    return UserUseCases(user_service)


async def get_service_use_cases(service_service: ServiceService = Depends(get_service_service)) -> ServiceUseCases:
    return ServiceUseCases(service_service)


async def get_category_use_cases(category_service: CategoryService = Depends(get_category_service)) -> CategoryUseCases:
    return CategoryUseCases(category_service)


async def get_availability_use_cases(
    availability_service: AvailabilityService = Depends(get_availability_service),
) -> AvailabilityUseCases:
    return AvailabilityUseCases(availability_service)


async def get_review_use_cases(
    review_service: ReviewService = Depends(get_review_service),
    rating_service: RatingService = Depends(get_rating_service),
    user_service: UserService = Depends(get_user_service),
) -> ReviewUseCases:
    return ReviewUseCases(review_service, rating_service, user_service)


async def get_chat_use_cases(chat_service: ChatService = Depends(get_chat_service)) -> ChatUseCases:
    return ChatUseCases(chat_service)


async def get_job_use_cases(job_service: JobService = Depends(get_job_service)) -> JobUseCases:
    return JobUseCases(job_service)


async def resolve_user_from_token(
    token: str,
    *,
    settings: Settings,
    auth_repository: AuthRepository,
    user_service: UserService,
) -> UserProfile:
    try:
        token_info = decode_access_token(token, secret_key=settings.secret_key or "dev-secret-change-me")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    email = token_info["sub"].strip().lower()
    credential = await auth_repository.get_credential_by_email(email)
    demo_user = DEMO_USERS.get(email)
    if credential:
        auth_user_id = credential.auth_user_id
    elif demo_user:
        auth_user_id = UserAuthId(demo_user["auth_user_id"])
    else:
        auth_user_id = _derive_auth_user_id(email)

    existing = await user_service.find_user_by_auth_user_id(auth_user_id)
    if existing:
        return existing

    name = demo_user["name"] if demo_user else token_info.get("name", "User")
    surname = demo_user["surname"] if demo_user else token_info.get("surname", "")
    role = UserRole(demo_user["role"] if demo_user else token_info.get("role", UserRole.client))
    raw_phone = demo_user["phone"] if demo_user else "+38970000000"
    city = demo_user["city"] if demo_user else None

    try:
        phone_vo = PhoneNumber(raw_phone)
    except ValueError:
        phone_vo = PhoneNumber("+38970000000")

    now = datetime.now(UTC)
    new_user = UserProfile(
        id=UserId(),
        auth_user_id=auth_user_id,
        name=name,
        surname=surname,
        phone=str(phone_vo),
        role=role,
        city=city,
        company_name=(
            " ".join(part for part in [name, surname, "Services"] if part) if role == UserRole.provider else None
        ),
        profile_metadata={"email": email},
        created_at=now,
        updated_at=now,
        last_login=now,
    )
    return await user_service.create_user_profile(new_user)


async def get_current_user(
    authorization: str | None = Header(default=None, convert_underscores=False),
    settings: Settings = Depends(get_settings),
    db_session: AsyncSession = Depends(get_db_session),
) -> UserProfile:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    factory = InfrastructureServiceFactory()
    auth_repository = factory.create_auth_repository(db_session)
    user_repository = factory.create_user_repository(db_session)
    user_service = factory.create_user_service(user_repository, cache=None)
    return await resolve_user_from_token(
        token,
        settings=settings,
        auth_repository=auth_repository,
        user_service=user_service,
    )


def get_image_storage() -> IImageStoragePort:
    settings = get_settings()
    return CloudinaryStorageAdapter(
        cloud_name=settings.cloudinary.cloud_name,
        api_key=settings.cloudinary.api_key,
        api_secret=settings.cloudinary.api_secret,
    )


ImageStorageDep = Annotated[IImageStoragePort, Depends(get_image_storage)]

"""
Test fixtures module - Abstraction layer for test data creation.

This module provides factory functions for creating test data without exposing
infrastructure implementation details to test files. This maintains hexagonal
architecture boundaries by keeping infrastructure imports isolated.
"""

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

# Infrastructure imports are isolated to this module only
from mano.infrastructure.database.models import (
    JobModel,
    UserProfileModel,
    CategoryModel,
    ServiceModel,
    AvailabilityModel,
)

# Default test constants
DEFAULT_AUTH_USER_ID = "00000000-0000-0000-0000-000000000001"
DEFAULT_PHONE = "+38970123456"
DEFAULT_CURRENCY = "MKD"
DEFAULT_PRICING_TYPE = "fixed"


async def create_test_user(
    db_session: AsyncSession,
    auth_user_id: str | None = None,
    name: str = "Test",
    surname: str = "User",
    phone: str = DEFAULT_PHONE,
    role: str = "client",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test user in the database.

    Args:
        db_session: Database session
        auth_user_id: Auth user ID (defaults to test constant)
        name: User's first name
        surname: User's surname
        phone: User's phone number
        role: User role (client/provider)
        **kwargs: Additional user fields

    Returns:
        Dictionary with user data (not ORM model to avoid leaking infrastructure)
    """
    user_id = str(uuid4())
    user = UserProfileModel(
        id=user_id,
        auth_user_id=auth_user_id or DEFAULT_AUTH_USER_ID,
        name=name,
        surname=surname,
        phone=phone,
        role=role,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        **kwargs,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return {
        "id": user.id,
        "auth_user_id": user.auth_user_id,
        "name": user.name,
        "surname": user.surname,
        "phone": user.phone,
        "role": user.role,
        "city": user.city,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
    }


async def create_test_provider(
    db_session: AsyncSession,
    auth_user_id: str | None = None,
    name: str = "Test",
    surname: str = "Provider",
    phone: str = DEFAULT_PHONE,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test provider (user with provider role).

    Args:
        db_session: Database session
        auth_user_id: Auth user ID (defaults to test constant)
        name: Provider's first name
        surname: Provider's surname
        phone: Provider's phone number
        **kwargs: Additional provider fields

    Returns:
        Dictionary with provider data
    """
    return await create_test_user(
        db_session=db_session,
        auth_user_id=auth_user_id,
        name=name,
        surname=surname,
        phone=phone,
        role="provider",
        **kwargs,
    )


async def create_test_category(
    db_session: AsyncSession,
    name_mk: str = "Plumbing",
    _name_sq: str = "Hidraulik",
    slug: str | None = None,
    is_active: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test category in the database.

    Args:
        db_session: Database session
        name_mk: Category name in Macedonian
        name_sq: Category name in Albanian
        slug: URL-friendly slug (auto-generated if not provided)
        is_active: Whether category is active
        **kwargs: Additional category fields

    Returns:
        Dictionary with category data
    """
    category_id = str(uuid4())
    category_slug = slug or name_mk.lower().replace(" ", "-")

    category = CategoryModel(
        id=category_id,
        name=name_mk,
        slug=category_slug,
        is_active=is_active,
        **kwargs,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    return {
        "id": category.id,
        "name_mk": category.name,
        "name_sq": "",
        "slug": category.slug,
        "is_active": category.is_active,
    }


async def create_test_service(
    db_session: AsyncSession,
    provider_id: str,
    category_id: str,
    title: str = "Test Service",
    description: str = "Test service description with minimum length",
    price: float = 100.0,
    currency: str = DEFAULT_CURRENCY,
    pricing_type: str = DEFAULT_PRICING_TYPE,
    is_active: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test service in the database.

    Args:
        db_session: Database session
        provider_id: ID of the provider user
        category_id: ID of the service category
        title: Service title
        description: Service description
        price: Service price
        currency: Currency code
        pricing_type: Pricing type (fixed/hourly/etc)
        is_active: Whether service is active
        **kwargs: Additional service fields

    Returns:
        Dictionary with service data
    """
    service_id = str(uuid4())

    service = ServiceModel(
        id=service_id,
        provider_id=provider_id,
        category_id=category_id,
        title=title,
        description=description,
        price=price,
        currency=currency,
        pricing_type=pricing_type,
        is_active=is_active,
        **kwargs,
    )
    db_session.add(service)
    await db_session.commit()
    await db_session.refresh(service)

    return {
        "id": service.id,
        "provider_id": service.provider_id,
        "category_id": service.category_id,
        "title": service.title,
        "description": service.description,
        "price": service.price,
        "currency": service.currency,
        "pricing_type": service.pricing_type,
        "is_active": service.is_active,
        "rating": service.rating,
        "review_count": service.review_count,
    }


async def create_test_availability(
    db_session: AsyncSession,
    provider_id: str,
    day_of_week: int = 1,
    start_time: str = "09:00",
    end_time: str = "17:00",
    is_available: bool = True,
    specific_date: datetime | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Create a test availability slot in the database.

    Args:
        db_session: Database session
        provider_id: Provider ID
        day_of_week: Day of week (0=Mon, 6=Sun)
        start_time: Start time in HH:MM
        end_time: End time in HH:MM
        is_available: Whether provider is available
        specific_date: Specific date override
        **kwargs: Additional availability fields

    Returns:
        Dictionary with availability data
    """
    availability_id = str(uuid4())
    availability = AvailabilityModel(
        id=availability_id,
        provider_id=provider_id,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        is_available=is_available,
        specific_date=specific_date,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        **kwargs,
    )
    db_session.add(availability)
    await db_session.commit()
    await db_session.refresh(availability)

    return {
        "id": availability.id,
        "provider_id": availability.provider_id,
        "day_of_week": availability.day_of_week,
        "start_time": availability.start_time,
        "end_time": availability.end_time,
        "is_available": availability.is_available,
        "specific_date": availability.specific_date,
    }


async def create_test_job(
    db_session: AsyncSession,
    customer_id: str,
    category_id: str,
    description: str = "Job description with enough detail",
    latitude: float = 41.9981,
    longitude: float = 21.4254,
    address: str = "Job Street 1",
    technician_id: str | None = None,
    status: str = "pending",
    **kwargs: Any,
) -> dict[str, Any]:
    """Create a test job in the database."""
    job_id = str(uuid4())
    job = JobModel(
        id=job_id,
        customer_id=customer_id,
        technician_id=technician_id,
        category_id=category_id,
        description=description,
        location=f"POINT ({longitude} {latitude})",
        address=address,
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        **kwargs,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    return {
        "id": job.id,
        "customer_id": job.customer_id,
        "technician_id": job.technician_id,
        "category_id": job.category_id,
        "description": job.description,
        "address": job.address,
        "status": job.status,
    }

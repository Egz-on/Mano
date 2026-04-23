"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import CHAR, TypeDecorator

from mano.common.constans import FieldLength


class LocationGeometry(TypeDecorator):
    """Use PostGIS geometry in PostgreSQL and plain text elsewhere."""

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry(geometry_type="POINT", srid=4326))
        return dialect.type_descriptor(Text())


LOCATION_TYPE = LocationGeometry()


class Base(DeclarativeBase):
    """Base declarative model."""


class GUID(TypeDecorator):
    """Enhanced GUID type that works with PostgreSQL and SQLite."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect: Any) -> Any:
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(String(FieldLength.UUID_STRING))

    def process_bind_param(self, value: Any, dialect: Any) -> str | None:
        _ = dialect
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, str):
            try:
                return str(uuid.UUID(value))
            except ValueError:
                return value
        return str(value)

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        _ = dialect
        return value


class UserProfileModel(Base):
    """User profiles table."""

    __tablename__ = "user_profiles"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(GUID, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    surname = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    phone = Column(String(20), nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    role = Column(String(20), nullable=False, default="client", index=True)
    city = Column(String(100), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    company_name = Column(String(255), nullable=True)
    business_hours = Column(JSON, nullable=True)
    profile_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)
    location = Column(LOCATION_TYPE, nullable=True)
    approval_status = Column(String(20), default="pending", nullable=False)
    fcm_token = Column(String(500), nullable=True)

    services = relationship("ServiceModel", back_populates="provider", cascade="all, delete-orphan")
    reviews_received = relationship("ReviewModel", foreign_keys="ReviewModel.provider_id", back_populates="provider")
    reviews_given = relationship("ReviewModel", foreign_keys="ReviewModel.client_id", back_populates="client")
    availability_slots = relationship("AvailabilityModel", back_populates="provider", cascade="all, delete-orphan")
    moderated_reviews = relationship("ReviewModel", foreign_keys="ReviewModel.moderated_by", back_populates="moderator")
    auth_credentials = relationship("AuthCredentialModel", cascade="all, delete-orphan")
    messages_sent = relationship("MessageModel", back_populates="sender")

    @property
    def full_name(self) -> str:
        parts = [self.name.strip(), self.surname.strip()]
        return " ".join(part for part in parts if part)

    @full_name.setter
    def full_name(self, value: str) -> None:
        normalized = value.strip()
        if not normalized:
            self.name = ""
            self.surname = ""
            return
        first_name, separator, remainder = normalized.partition(" ")
        self.name = first_name
        self.surname = remainder if separator else ""

    def __repr__(self) -> str:
        return f"<UserProfile {self.full_name} - {self.role}>"


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    job_id = Column(GUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, unique=True, index=True)
    job = relationship("JobModel", back_populates="conversation")

    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(GUID, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(GUID, ForeignKey("user_profiles.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)

    conversation = relationship("ConversationModel", back_populates="messages")
    sender = relationship("UserProfileModel", back_populates="messages_sent")


class CategoryModel(Base):
    """Categories table."""

    __tablename__ = "categories"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    icon = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    parent_id = Column(GUID, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    parent = relationship("CategoryModel", remote_side=[id], backref="subcategories")
    services = relationship("ServiceModel", back_populates="category")


class ServiceModel(Base):
    """Services table."""

    __tablename__ = "services"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    provider_id = Column(GUID, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(GUID, ForeignKey("categories.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="MKD")
    pricing_type = Column(String(50), nullable=False, default="fixed")
    service_areas = Column(JSON, nullable=True)
    service_metadata = Column(JSON, nullable=True)
    images = Column(JSON, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    provider = relationship("UserProfileModel", back_populates="services")
    category = relationship("CategoryModel", back_populates="services")
    reviews = relationship("ReviewModel", back_populates="service", cascade="all, delete-orphan")


class ReviewModel(Base):
    """Reviews table."""

    __tablename__ = "reviews"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID, ForeignKey("user_profiles.id"), nullable=False, index=True)
    provider_id = Column(GUID, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(GUID, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(GUID, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    images = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    moderated_by = Column(GUID, ForeignKey("user_profiles.id"), nullable=True, index=True)
    moderated_at = Column(DateTime(timezone=True), nullable=True)
    moderation_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    client = relationship("UserProfileModel", foreign_keys=[client_id], back_populates="reviews_given")
    provider = relationship("UserProfileModel", foreign_keys=[provider_id], back_populates="reviews_received")
    service = relationship("ServiceModel", back_populates="reviews")
    moderator = relationship("UserProfileModel", foreign_keys=[moderated_by], back_populates="moderated_reviews")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_rating_range"),
        CheckConstraint("status IN ('pending', 'approved', 'rejected')", name="chk_status_values"),
        UniqueConstraint("client_id", "job_id", name="uq_one_review_per_job"),
    )


class AvailabilityModel(Base):
    """Availability table."""

    __tablename__ = "availability"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    provider_id = Column(GUID, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    is_available = Column(Boolean, default=True)
    specific_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    provider = relationship("UserProfileModel", back_populates="availability_slots")


class AuthCredentialModel(Base):
    """Local auth credentials table."""

    __tablename__ = "auth_credentials"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(
        GUID,
        ForeignKey("user_profiles.auth_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,
    )
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class PasswordResetTokenModel(Base):
    """Password reset tokens table."""

    __tablename__ = "password_reset_tokens"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(
        GUID,
        ForeignKey("auth_credentials.auth_user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash = Column(String(128), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True, index=True)


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    customer_id = Column(GUID, ForeignKey("user_profiles.id"), nullable=False, index=True)
    technician_id = Column(GUID, ForeignKey("user_profiles.id"), nullable=True, index=True)
    category_id = Column(GUID, ForeignKey("categories.id"), nullable=False, index=True)

    description = Column(Text, nullable=False)
    photo_urls = Column(JSON, nullable=True)
    location = Column(LOCATION_TYPE, nullable=False)
    address = Column(String(500), nullable=False)  # ← display only

    status = Column(String(30), nullable=False, default="pending", index=True)
    call_out_fee_paid = Column(Boolean, default=False, nullable=False)
    chat_unlocked = Column(Boolean, default=False, nullable=False)

    quote_amount = Column(String(20), nullable=True)  # ← String not Float
    quote_description = Column(Text, nullable=True)
    quote_submitted_at = Column(DateTime(timezone=True), nullable=True)
    quote_approved_at = Column(DateTime(timezone=True), nullable=True)
    quote_rejected_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    customer = relationship("UserProfileModel", foreign_keys=[customer_id])
    technician = relationship("UserProfileModel", foreign_keys=[technician_id])
    category = relationship("CategoryModel")
    conversation = relationship("ConversationModel", back_populates="job", uselist=False)

    __table_args__ = (
        CheckConstraint(
            "status IN ("
            "'pending','assigned','en_route','arrived',"
            "'diagnosed','quote_approved','quote_rejected',"
            "'in_progress','completed','cancelled'"
            ")",
            name="chk_job_status",
        ),
    )

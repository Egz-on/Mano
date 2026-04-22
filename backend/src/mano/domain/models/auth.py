"""Auth domain models."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
import uuid

from mano.domain.models.user import UserAuthId, UserProfile


@dataclass(frozen=True)
class AuthCredentialId:
    """Identifier for local auth credentials."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PasswordResetTokenId:
    """Identifier for password reset tokens."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AuthCredential:
    """Local authentication credentials for a user."""

    id: AuthCredentialId
    auth_user_id: UserAuthId
    email: str
    password_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        normalized_email = self.email.strip().lower()
        if "@" not in normalized_email:
            raise ValueError("Invalid email")

        object.__setattr__(self, "email", normalized_email)


@dataclass(frozen=True)
class PasswordResetToken:
    """Password reset token stored in hashed form."""

    id: PasswordResetTokenId
    auth_user_id: UserAuthId
    token_hash: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    used_at: datetime | None = None

    def is_active(self, now: datetime) -> bool:
        """Return True if the token can still be used."""
        return self.used_at is None and self.expires_at > now

    def mark_used(self, used_at: datetime) -> PasswordResetToken:
        """Return a new token marked as used."""
        return replace(self, used_at=used_at)


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """Authenticated principal returned by auth flows."""

    email: str
    user: UserProfile

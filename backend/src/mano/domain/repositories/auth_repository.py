"""Local auth repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from mano.domain.models.auth import AuthCredential, PasswordResetToken, PasswordResetTokenId
from mano.domain.models.user import UserAuthId


class AuthRepository(ABC):
    """Persistence contract for local auth data."""

    @abstractmethod
    async def get_credential_by_email(self, email: str) -> AuthCredential | None:
        """Fetch a credential by normalized email."""

    @abstractmethod
    async def create_credential(self, credential: AuthCredential) -> AuthCredential:
        """Persist a new credential."""

    @abstractmethod
    async def update_credential_password(
        self,
        auth_user_id: UserAuthId,
        password_hash: str,
        updated_at: datetime,
    ) -> None:
        """Update the password hash for a user."""

    @abstractmethod
    async def create_password_reset_token(self, reset_token: PasswordResetToken) -> PasswordResetToken:
        """Persist a new password reset token."""

    @abstractmethod
    async def get_active_password_reset_token(self, token_hash: str, at_time: datetime) -> PasswordResetToken | None:
        """Fetch a non-expired, unused password reset token."""

    @abstractmethod
    async def invalidate_active_password_reset_tokens(self, auth_user_id: UserAuthId, used_at: datetime) -> None:
        """Invalidate all still-active reset tokens for a user."""

    @abstractmethod
    async def mark_password_reset_token_used(self, token_id: PasswordResetTokenId, used_at: datetime) -> None:
        """Mark a specific password reset token as used."""

"""Auth domain service."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from uuid import NAMESPACE_DNS, uuid5

from mano.domain.exceptions.base import EmailAlreadyRegisteredError, InvalidPasswordResetTokenError
from mano.domain.models.auth import (
    AuthCredential,
    AuthCredentialId,
    AuthenticatedPrincipal,
    PasswordResetToken,
    PasswordResetTokenId,
)
from mano.domain.models.user import PhoneNumber, UserAuthId, UserId, UserProfile, UserRole
from mano.domain.repositories.auth_repository import AuthRepository
from mano.domain.repositories.password_hasher_port import PasswordHasherPort
from mano.domain.services.user_service import UserService


class AuthService:
    """Domain service coordinating local authentication flows."""

    RESET_TOKEN_TTL_MINUTES = 30

    def __init__(
        self,
        auth_repository: AuthRepository,
        user_service: UserService,
        password_hasher: PasswordHasherPort,
    ) -> None:
        self.auth_repository = auth_repository
        self.user_service = user_service
        self.password_hasher = password_hasher

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        phone: str,
        role: UserRole,
        city: str | None,
        company_name: str | None,
    ) -> AuthenticatedPrincipal:
        """Register a local user and credentials."""
        normalized_email = email.strip().lower()
        existing_credential = await self.auth_repository.get_credential_by_email(normalized_email)
        if existing_credential:
            raise EmailAlreadyRegisteredError("Email is already registered")

        auth_user_id = UserAuthId(str(uuid5(NAMESPACE_DNS, f"mano:{normalized_email}")))

        existing_user = await self.user_service.user_repository.get_user_by_auth_user_id(auth_user_id)
        if existing_user:
            raise EmailAlreadyRegisteredError("Email is already registered")

        user_phone = str(PhoneNumber(phone))
        provider_company_name = company_name
        if role == UserRole.provider and not provider_company_name:
            provider_company_name = f"{full_name} Services"

        now = datetime.now(UTC)
        user = UserProfile(
            id=UserId(),
            auth_user_id=auth_user_id,
            full_name=full_name,
            phone=user_phone,
            role=role,
            city=city,
            company_name=provider_company_name,
            profile_metadata={"email": normalized_email},
            created_at=now,
            updated_at=now,
            last_login=now,
        )
        created_user = await self.user_service.create_user_profile(user)

        credential = AuthCredential(
            id=AuthCredentialId(),
            auth_user_id=auth_user_id,
            email=normalized_email,
            password_hash=self.password_hasher.hash_password(password),
            created_at=now,
            updated_at=now,
        )
        await self.auth_repository.create_credential(credential)

        return AuthenticatedPrincipal(email=normalized_email, user=created_user)

    async def authenticate(self, *, email: str, password: str) -> AuthenticatedPrincipal | None:
        """Authenticate user by local credentials."""
        normalized_email = email.strip().lower()
        credential = await self.auth_repository.get_credential_by_email(normalized_email)
        if not credential:
            return None

        if not self.password_hasher.verify_password(password, credential.password_hash):
            return None

        user = await self.user_service.get_user_by_auth_user_id(credential.auth_user_id)
        updated_user = await self.user_service.update_user_profile(user.update_last_login())

        return AuthenticatedPrincipal(email=normalized_email, user=updated_user)

    async def request_password_reset(self, *, email: str) -> str | None:
        """Issue password reset token for an existing account."""
        normalized_email = email.strip().lower()
        credential = await self.auth_repository.get_credential_by_email(normalized_email)
        if not credential:
            return None

        now = datetime.now(UTC)
        await self.auth_repository.invalidate_active_password_reset_tokens(credential.auth_user_id, now)

        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        reset_token = PasswordResetToken(
            id=PasswordResetTokenId(),
            auth_user_id=credential.auth_user_id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=self.RESET_TOKEN_TTL_MINUTES),
            created_at=now,
        )
        await self.auth_repository.create_password_reset_token(reset_token)

        return raw_token

    async def reset_password(self, *, token: str, new_password: str) -> None:
        """Reset password using one-time reset token."""
        now = datetime.now(UTC)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        reset_token = await self.auth_repository.get_active_password_reset_token(token_hash, now)
        if not reset_token:
            raise InvalidPasswordResetTokenError("Reset token is invalid or expired")

        password_hash = self.password_hasher.hash_password(new_password)
        await self.auth_repository.update_credential_password(reset_token.auth_user_id, password_hash, now)
        await self.auth_repository.mark_password_reset_token_used(reset_token.id, now)
        await self.auth_repository.invalidate_active_password_reset_tokens(reset_token.auth_user_id, now)

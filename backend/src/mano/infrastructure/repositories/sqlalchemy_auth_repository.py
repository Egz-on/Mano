"""SQLAlchemy auth repository implementation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mano.domain.models.auth import (
    AuthCredential,
    AuthCredentialId,
    PasswordResetToken,
    PasswordResetTokenId,
)
from mano.domain.models.user import UserAuthId
from mano.domain.repositories.auth_repository import AuthRepository
from mano.infrastructure.database.models import AuthCredentialModel, PasswordResetTokenModel


class SQLAlchemyAuthRepository(AuthRepository):
    """SQLAlchemy-backed implementation of AuthRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _credential_to_domain(model: AuthCredentialModel) -> AuthCredential:
        return AuthCredential(
            id=AuthCredentialId(str(model.id)),
            auth_user_id=UserAuthId(str(model.auth_user_id)),
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _reset_token_to_domain(model: PasswordResetTokenModel) -> PasswordResetToken:
        return PasswordResetToken(
            id=PasswordResetTokenId(str(model.id)),
            auth_user_id=UserAuthId(str(model.auth_user_id)),
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            used_at=model.used_at,
        )

    async def get_credential_by_email(self, email: str) -> AuthCredential | None:
        stmt = select(AuthCredentialModel).where(AuthCredentialModel.email == email.strip().lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._credential_to_domain(model) if model else None

    async def create_credential(self, credential: AuthCredential) -> AuthCredential:
        model = AuthCredentialModel(
            id=str(credential.id),
            auth_user_id=str(credential.auth_user_id),
            email=credential.email,
            password_hash=credential.password_hash,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._credential_to_domain(model)

    async def update_credential_password(self, auth_user_id: UserAuthId, password_hash: str, updated_at: datetime) -> None:
        stmt = (
            update(AuthCredentialModel)
            .where(AuthCredentialModel.auth_user_id == str(auth_user_id))
            .values(password_hash=password_hash, updated_at=updated_at)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def create_password_reset_token(self, reset_token: PasswordResetToken) -> PasswordResetToken:
        model = PasswordResetTokenModel(
            id=str(reset_token.id),
            auth_user_id=str(reset_token.auth_user_id),
            token_hash=reset_token.token_hash,
            expires_at=reset_token.expires_at,
            created_at=reset_token.created_at,
            used_at=reset_token.used_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._reset_token_to_domain(model)

    async def get_active_password_reset_token(self, token_hash: str, at_time: datetime) -> PasswordResetToken | None:
        stmt = (
            select(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.token_hash == token_hash)
            .where(PasswordResetTokenModel.used_at.is_(None))
            .where(PasswordResetTokenModel.expires_at > at_time)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._reset_token_to_domain(model) if model else None

    async def invalidate_active_password_reset_tokens(self, auth_user_id: UserAuthId, used_at: datetime) -> None:
        stmt = (
            update(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.auth_user_id == str(auth_user_id))
            .where(PasswordResetTokenModel.used_at.is_(None))
            .where(PasswordResetTokenModel.expires_at > used_at)
            .values(used_at=used_at)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def mark_password_reset_token_used(self, token_id: PasswordResetTokenId, used_at: datetime) -> None:
        stmt = update(PasswordResetTokenModel).where(PasswordResetTokenModel.id == str(token_id)).values(used_at=used_at)
        await self._session.execute(stmt)
        await self._session.flush()

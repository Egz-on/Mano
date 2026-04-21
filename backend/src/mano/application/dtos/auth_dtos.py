"""Auth DTOs for application layer."""

from __future__ import annotations

from dataclasses import dataclass

from mano.domain.models.user import UserRole


@dataclass(frozen=True)
class RegisterRequest:
    """DTO for user registration."""

    email: str
    password: str
    full_name: str
    phone: str
    role: UserRole = UserRole.client
    city: str | None = None
    company_name: str | None = None


@dataclass(frozen=True)
class LoginRequestDTO:
    """DTO for local login."""

    email: str
    password: str


@dataclass(frozen=True)
class ForgotPasswordRequest:
    """DTO for forgot password flow."""

    email: str


@dataclass(frozen=True)
class ResetPasswordRequest:
    """DTO for reset password flow."""

    token: str
    new_password: str


@dataclass(frozen=True)
class AuthenticatedUserDTO:
    """DTO representing authenticated user claims."""

    email: str
    full_name: str
    role: str

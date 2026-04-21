"""Auth use cases."""

from __future__ import annotations

from urllib.parse import urlencode

from workmate.application.dtos.auth_dtos import (
    AuthenticatedUserDTO,
    ForgotPasswordRequest,
    LoginRequestDTO,
    RegisterRequest,
    ResetPasswordRequest,
)
from workmate.domain.models.user import UserRole
from workmate.domain.repositories.email_sender_port import EmailSenderPort
from workmate.domain.services.auth_service import AuthService


class AuthUseCases:
    """Application use cases for local authentication."""

    def __init__(
        self,
        auth_service: AuthService,
        email_sender: EmailSenderPort,
        frontend_url: str,
    ) -> None:
        self.auth_service = auth_service
        self.email_sender = email_sender
        self.frontend_url = frontend_url.rstrip("/")

    async def register(self, request: RegisterRequest) -> AuthenticatedUserDTO:
        """Register a user and return auth-ready claims."""
        principal = await self.auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
            role=request.role,
            city=request.city,
            company_name=request.company_name,
        )
        return AuthenticatedUserDTO(
            email=principal.email,
            full_name=principal.user.full_name,
            role=str(principal.user.role),
        )

    async def login(self, request: LoginRequestDTO) -> AuthenticatedUserDTO | None:
        """Login using local credentials."""
        principal = await self.auth_service.authenticate(email=request.email, password=request.password)
        if principal is None:
            return None

        return AuthenticatedUserDTO(
            email=principal.email,
            full_name=principal.user.full_name,
            role=str(principal.user.role),
        )

    async def forgot_password(self, request: ForgotPasswordRequest) -> str | None:
        """Request a password reset token for existing account."""
        reset_token = await self.auth_service.request_password_reset(email=request.email)
        if not reset_token:
            return None

        reset_url = self._build_reset_password_url(token=reset_token)
        await self.email_sender.send_email(
            recipient=request.email,
            subject="Reset your Workmate password",
            text_body=self._build_reset_password_text(reset_url=reset_url),
            html_body=self._build_reset_password_html(reset_url=reset_url),
        )

        return reset_token

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        """Reset account password using one-time token."""
        await self.auth_service.reset_password(token=request.token, new_password=request.new_password)

    @staticmethod
    def parse_role(raw_role: str) -> UserRole:
        """Parse incoming role string into domain role enum."""
        return UserRole(raw_role)

    def _build_reset_password_url(self, *, token: str) -> str:
        query = urlencode({"token": token})
        return f"{self.frontend_url}/reset-password?{query}"

    @staticmethod
    def _build_reset_password_text(*, reset_url: str) -> str:
        return (
            "You requested a password reset for your Workmate account.\n\n"
            f"Reset your password: {reset_url}\n\n"
            "This link expires in 30 minutes. If you did not request this, you can ignore this email."
        )

    @staticmethod
    def _build_reset_password_html(*, reset_url: str) -> str:
        return f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #111827; line-height: 1.6;">
    <h2 style="margin-bottom: 12px;">Reset your Workmate password</h2>
    <p>You requested a password reset for your Workmate account.</p>
    <p style="margin: 24px 0;">
      <a
        href="{reset_url}"
        style="background: #0f766e; color: white; text-decoration: none; padding: 12px 18px; border-radius: 8px; display: inline-block;"
      >
        Reset password
      </a>
    </p>
    <p>If the button does not work, use this link:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>This link expires in 30 minutes. If you did not request this, you can ignore this email.</p>
  </body>
</html>
""".strip()

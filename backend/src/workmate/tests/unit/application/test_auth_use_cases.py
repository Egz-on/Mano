from unittest.mock import AsyncMock

import pytest

from workmate.application.dtos.auth_dtos import ForgotPasswordRequest
from workmate.application.use_cases.auth_use_cases import AuthUseCases
from workmate.domain.repositories.email_sender_port import EmailSenderPort
from workmate.domain.services.auth_service import AuthService


class TestAuthUseCases:
    @pytest.fixture
    def mock_auth_service(self) -> AsyncMock:
        return AsyncMock(spec=AuthService)

    @pytest.fixture
    def mock_email_sender(self) -> AsyncMock:
        return AsyncMock(spec=EmailSenderPort)

    @pytest.fixture
    def use_cases(self, mock_auth_service: AsyncMock, mock_email_sender: AsyncMock) -> AuthUseCases:
        return AuthUseCases(
            auth_service=mock_auth_service,
            email_sender=mock_email_sender,
            frontend_url="http://localhost:3000",
        )

    @pytest.mark.asyncio
    async def test_forgot_password_sends_reset_email(
        self,
        use_cases: AuthUseCases,
        mock_auth_service: AsyncMock,
        mock_email_sender: AsyncMock,
    ) -> None:
        mock_auth_service.request_password_reset.return_value = "reset-token-123"

        result = await use_cases.forgot_password(ForgotPasswordRequest(email="user@example.com"))

        assert result == "reset-token-123"
        mock_email_sender.send_email.assert_awaited_once()
        call = mock_email_sender.send_email.await_args
        assert call.kwargs["recipient"] == "user@example.com"
        assert call.kwargs["subject"] == "Reset your Workmate password"
        assert "http://localhost:3000/reset-password?token=reset-token-123" in call.kwargs["text_body"]
        assert "http://localhost:3000/reset-password?token=reset-token-123" in (call.kwargs["html_body"] or "")

    @pytest.mark.asyncio
    async def test_forgot_password_skips_email_when_account_missing(
        self,
        use_cases: AuthUseCases,
        mock_auth_service: AsyncMock,
        mock_email_sender: AsyncMock,
    ) -> None:
        mock_auth_service.request_password_reset.return_value = None

        result = await use_cases.forgot_password(ForgotPasswordRequest(email="missing@example.com"))

        assert result is None
        mock_email_sender.send_email.assert_not_awaited()

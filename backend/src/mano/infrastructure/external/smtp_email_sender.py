"""SMTP email sender implementation."""

from __future__ import annotations

import asyncio
from email.message import EmailMessage
from email.utils import formataddr
import smtplib

from mano.domain.exceptions.base import EmailDeliveryError
from mano.domain.repositories.email_sender_port import EmailSenderPort


class SMTPEmailSender(EmailSenderPort):
    """Send emails using a configured SMTP server such as Mailpit."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        sender_email: str,
        sender_name: str,
        username: str | None = None,
        password: str | None = None,
        use_tls: bool = False,
        use_starttls: bool = False,
        timeout: float = 10.0,
    ) -> None:
        self.host = host
        self.port = port
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_starttls = use_starttls
        self.timeout = timeout

    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        await asyncio.to_thread(
            self._send_email_sync,
            recipient=recipient,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )

    def _send_email_sync(
        self,
        *,
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = formataddr((self.sender_name, self.sender_email))
        message["To"] = recipient
        message.set_content(text_body)

        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            if self.use_tls:
                with smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout) as smtp:
                    self._authenticate_and_send(smtp, message)
                return

            with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as smtp:
                smtp.ehlo()
                if self.use_starttls:
                    smtp.starttls()
                    smtp.ehlo()
                self._authenticate_and_send(smtp, message)
        except (OSError, smtplib.SMTPException) as exc:
            raise EmailDeliveryError("Could not send password reset email") from exc

    def _authenticate_and_send(self, smtp: smtplib.SMTP, message: EmailMessage) -> None:
        if self.username and self.password:
            smtp.login(self.username, self.password)
        smtp.send_message(message)

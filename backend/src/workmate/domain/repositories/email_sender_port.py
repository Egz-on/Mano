"""Email delivery port."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSenderPort(ABC):
    """Abstraction for sending transactional emails."""

    @abstractmethod
    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        """Deliver an email message."""
        ...

"""Chat domain exceptions."""

from __future__ import annotations

from mano.domain.exceptions.base import DomainError


class ConversationNotFoundError(DomainError):
    """Conversation does not exist."""


class MessageValidationError(DomainError):
    """Message payload is invalid."""

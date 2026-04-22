"""Chat domain exceptions."""

from __future__ import annotations

from mano.domain.exceptions.base import DomainError


class ConversationNotFoundError(DomainError):
    """Conversation does not exist."""


class ConversationAccessDeniedError(DomainError):
    """User is not allowed to access this conversation."""


class ConversationLockedError(DomainError):
    """Conversation is locked until in-app payment completes."""


class InvalidConversationParticipantsError(DomainError):
    """Conversation participants do not satisfy the product rules."""


class MessageValidationError(DomainError):
    """Message payload is invalid."""

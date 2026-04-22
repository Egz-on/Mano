"""Chat application DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from mano.domain.models.conversation import ConversationId
from mano.domain.models.user import UserId


@dataclass(frozen=True)
class CreateMessageRequest:
    """Input DTO for creating a chat message."""

    conversation_id: ConversationId
    sender_id: UserId
    content: str


@dataclass(frozen=True)
class ListMessagesRequest:
    """Input DTO for fetching paginated message history."""

    conversation_id: ConversationId
    limit: int = 50
    offset: int = 0

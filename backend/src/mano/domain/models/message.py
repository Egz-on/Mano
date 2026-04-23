"""Message domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import uuid

from mano.domain.exceptions.chat_exceptions import MessageValidationError
from mano.domain.models.conversation import ConversationId
from mano.domain.models.user import UserId


@dataclass(frozen=True)
class MessageId:
    """Message identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Message:
    """Immutable chat message entity."""

    id: MessageId
    conversation_id: ConversationId
    sender_id: UserId
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        normalized_content = self.content.strip()
        if not normalized_content:
            raise MessageValidationError("Message content cannot be empty")
        if len(normalized_content) > 4000:
            raise MessageValidationError("Message content must be 4000 characters or less")
        object.__setattr__(self, "content", normalized_content)

    @classmethod
    def create(
        cls,
        *,
        conversation_id: ConversationId,
        sender_id: UserId,
        content: str,
    ) -> Message:
        return cls(
            id=MessageId(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            created_at=datetime.now(UTC),
        )

"""Chat repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mano.domain.models.conversation import Conversation, ConversationId
from mano.domain.models.message import Message


class ChatRepository(ABC):
    """Abstract chat repository."""

    @abstractmethod
    async def create_conversation(self, conversation: Conversation) -> Conversation:
        """Persist a new conversation."""

    @abstractmethod
    async def get_conversation(self, conversation_id: ConversationId) -> Conversation | None:
        """Return a conversation by ID."""

    @abstractmethod
    async def create_message(self, message: Message) -> Message:
        """Persist a new chat message."""

    @abstractmethod
    async def list_messages(
        self,
        conversation_id: ConversationId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        """List messages for a conversation ordered by creation time."""

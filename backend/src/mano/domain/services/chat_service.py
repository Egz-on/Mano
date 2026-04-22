"""Chat domain service implementation."""

from __future__ import annotations

from mano.domain.exceptions.chat_exceptions import ConversationNotFoundError
from mano.domain.models.conversation import Conversation, ConversationId
from mano.domain.models.message import Message
from mano.domain.repositories.chat_repository import ChatRepository


class ChatService:
    """Coordinates conversation and message persistence."""

    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        return await self.chat_repository.create_conversation(conversation)

    async def get_conversation(self, conversation_id: ConversationId) -> Conversation:
        conversation = await self.chat_repository.get_conversation(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(f"Conversation {conversation_id} not found")
        return conversation

    async def list_messages(
        self,
        conversation_id: ConversationId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        await self.get_conversation(conversation_id)
        return await self.chat_repository.list_messages(conversation_id, limit=limit, offset=offset)

    async def create_message(self, message: Message) -> Message:
        await self.get_conversation(message.conversation_id)
        return await self.chat_repository.create_message(message)

"""Chat application use cases."""

from __future__ import annotations

from mano.application.dtos.chat_dtos import CreateMessageRequest, ListMessagesRequest
from mano.domain.models.conversation import Conversation
from mano.domain.models.message import Message
from mano.domain.services.chat_service import ChatService


class ChatUseCases:
    """Application-level orchestration for chat flows."""

    def __init__(self, chat_service: ChatService) -> None:
        self.chat_service = chat_service

    async def create_conversation(self) -> Conversation:
        return await self.chat_service.create_conversation(Conversation.create())

    async def get_conversation(self, conversation_id: str) -> Conversation:
        from mano.domain.models.conversation import ConversationId

        return await self.chat_service.get_conversation(ConversationId(conversation_id))

    async def list_messages(self, request: ListMessagesRequest) -> list[Message]:
        return await self.chat_service.list_messages(
            request.conversation_id,
            limit=request.limit,
            offset=request.offset,
        )

    async def create_message(self, request: CreateMessageRequest) -> Message:
        message = Message.create(
            conversation_id=request.conversation_id,
            sender_id=request.sender_id,
            content=request.content,
        )
        return await self.chat_service.create_message(message)

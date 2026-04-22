"""SQLAlchemy chat repository implementation."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mano.common.uuid_utils import uuid_to_str
from mano.domain.models.conversation import Conversation, ConversationId
from mano.domain.models.message import Message, MessageId
from mano.domain.models.user import UserId
from mano.domain.repositories.chat_repository import ChatRepository
from mano.infrastructure.database.models import ConversationModel, MessageModel


class SQLAlchemyChatRepository(ChatRepository):
    """Persist chat conversations and messages with SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _conversation_to_domain(model: ConversationModel) -> Conversation:
        return Conversation(
            id=ConversationId(str(model.id)),
            created_at=model.created_at,
        )

    @staticmethod
    def _message_to_domain(model: MessageModel) -> Message:
        return Message(
            id=MessageId(str(model.id)),
            conversation_id=ConversationId(str(model.conversation_id)),
            sender_id=UserId(str(model.sender_id)),
            content=model.content,
            created_at=model.created_at,
        )

    async def create_conversation(self, conversation: Conversation) -> Conversation:
        model = ConversationModel(
            id=uuid_to_str(conversation.id),
            created_at=conversation.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._conversation_to_domain(model)

    async def get_conversation(self, conversation_id: ConversationId) -> Conversation | None:
        stmt = select(ConversationModel).where(ConversationModel.id == uuid_to_str(conversation_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._conversation_to_domain(model) if model else None

    async def create_message(self, message: Message) -> Message:
        model = MessageModel(
            id=uuid_to_str(message.id),
            conversation_id=uuid_to_str(message.conversation_id),
            sender_id=uuid_to_str(message.sender_id),
            content=message.content,
            created_at=message.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._message_to_domain(model)

    async def list_messages(
        self,
        conversation_id: ConversationId,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == uuid_to_str(conversation_id))
            .order_by(MessageModel.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [self._message_to_domain(model) for model in result.scalars().all()]

"""Chat REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mano.application.dtos.chat_dtos import CreateMessageRequest, ListMessagesRequest
from mano.application.use_cases.chat_use_cases import ChatUseCases
from mano.dependencies import get_chat_use_cases, get_current_user
from mano.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageValidationError
from mano.domain.models.conversation import Conversation, ConversationId
from mano.domain.models.message import Message
from mano.domain.models.user import UserId, UserProfile
from mano.presentation.schemas.chat_schemas import (
    ChatMessageCreateSchema,
    ChatMessageResponseSchema,
    ConversationResponseSchema,
)

router = APIRouter(prefix="/conversations", tags=["chat"])


def _conversation_to_response(conversation: Conversation) -> ConversationResponseSchema:
    return ConversationResponseSchema(
        id=UUID(str(conversation.id)),
        created_at=conversation.created_at,
    )


def _message_to_response(message: Message) -> ChatMessageResponseSchema:
    return ChatMessageResponseSchema(
        id=UUID(str(message.id)),
        conversation_id=UUID(str(message.conversation_id)),
        sender_id=UUID(str(message.sender_id)),
        content=message.content,
        created_at=message.created_at,
    )


@router.post("/", response_model=ConversationResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    current_user: UserProfile = Depends(get_current_user),
    use_case: ChatUseCases = Depends(get_chat_use_cases),
) -> ConversationResponseSchema:
    _ = current_user
    conversation = await use_case.create_conversation()
    return _conversation_to_response(conversation)


@router.get("/{conversation_id}", response_model=ConversationResponseSchema)
async def get_conversation(
    conversation_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    use_case: ChatUseCases = Depends(get_chat_use_cases),
) -> ConversationResponseSchema:
    _ = current_user
    try:
        conversation = await use_case.get_conversation(str(conversation_id))
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _conversation_to_response(conversation)


@router.get("/{conversation_id}/messages", response_model=list[ChatMessageResponseSchema])
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_user: UserProfile = Depends(get_current_user),
    use_case: ChatUseCases = Depends(get_chat_use_cases),
) -> list[ChatMessageResponseSchema]:
    _ = current_user
    try:
        messages = await use_case.list_messages(
            ListMessagesRequest(
                conversation_id=ConversationId(str(conversation_id)),
                limit=limit,
                offset=offset,
            )
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [_message_to_response(message) for message in messages]


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatMessageResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: UUID,
    payload: ChatMessageCreateSchema,
    current_user: UserProfile = Depends(get_current_user),
    use_case: ChatUseCases = Depends(get_chat_use_cases),
) -> ChatMessageResponseSchema:
    try:
        message = await use_case.create_message(
            CreateMessageRequest(
                conversation_id=ConversationId(str(conversation_id)),
                sender_id=UserId(str(current_user.id)),
                content=payload.content,
            )
        )
    except ConversationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MessageValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _message_to_response(message)

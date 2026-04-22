"""Realtime chat websocket endpoint."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from mano.application.dtos.chat_dtos import CreateMessageRequest
from mano.application.use_cases.chat_use_cases import ChatUseCases
from mano.dependencies import (
    get_chat_use_cases,
    get_db_session,
    get_settings,
    resolve_user_from_token,
)
from mano.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageValidationError
from mano.domain.models.conversation import ConversationId
from mano.domain.models.user import UserId
from mano.infrastructure.config.settings import Settings
from mano.infrastructure.factories import InfrastructureServiceFactory
from mano.presentation.api.v1.chat_route import _message_to_response
from mano.presentation.schemas.chat_schemas import ChatSocketMessageSchema
from mano.presentation.websockets.chat import chat_connection_manager, chat_redis_bridge

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: UUID,
    db_session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
    use_case: ChatUseCases = Depends(get_chat_use_cases),
) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    try:
        factory = InfrastructureServiceFactory()
        auth_repository = factory.create_auth_repository(db_session)
        user_repository = factory.create_user_repository(db_session)
        user_service = factory.create_user_service(user_repository, cache=None)
        current_user = await resolve_user_from_token(
            token,
            settings=settings,
            auth_repository=auth_repository,
            user_service=user_service,
        )
        await use_case.get_conversation(str(conversation_id))
    except Exception as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return

    room_id = str(conversation_id)
    await chat_connection_manager.connect(room_id, websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            content = payload.get("content") if isinstance(payload, dict) else None

            if not isinstance(content, str):
                await websocket.send_json({"type": "error", "detail": "Payload must include string field 'content'"})
                continue

            try:
                message = await use_case.create_message(
                    CreateMessageRequest(
                        conversation_id=ConversationId(room_id),
                        sender_id=UserId(str(current_user.id)),
                        content=content,
                    )
                )
                await db_session.commit()
            except ConversationNotFoundError as exc:
                await db_session.rollback()
                await websocket.send_json({"type": "error", "detail": str(exc)})
                continue
            except MessageValidationError as exc:
                await db_session.rollback()
                await websocket.send_json({"type": "error", "detail": str(exc)})
                continue
            except Exception:
                await db_session.rollback()
                raise

            outbound = ChatSocketMessageSchema(message=_message_to_response(message)).model_dump(mode="json")
            await chat_redis_bridge.fanout(room_id, outbound)
    except WebSocketDisconnect:
        pass
    finally:
        await chat_connection_manager.disconnect(room_id, websocket)

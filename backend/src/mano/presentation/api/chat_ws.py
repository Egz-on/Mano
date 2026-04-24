"""Realtime chat websocket endpoint."""

from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from mano.dependencies import (
    Settings,
    create_ws_message,
    ensure_ws_conversation_exists,
    get_settings,
    resolve_ws_user,
)
from mano.domain.exceptions.chat_exceptions import ConversationNotFoundError, MessageValidationError
from mano.domain.models.user import UserId
from mano.presentation.api.v1.chat_route import _message_to_response
from mano.presentation.schemas.chat_schemas import ChatSocketMessageSchema
from mano.presentation.websockets.chat import chat_connection_manager, chat_redis_bridge

router = APIRouter(tags=["chat"])
logger = structlog.get_logger(__name__)


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: UUID,
    settings: Settings = Depends(get_settings),
) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    try:
        current_user = await resolve_ws_user(token, settings)
        room_id = str(conversation_id)
        await ensure_ws_conversation_exists(room_id)
    except ConversationNotFoundError as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc))
        return
    except Exception:
        logger.exception("websocket_auth_failed", conversation_id=str(conversation_id))
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Unable to authorize websocket")
        return

    await chat_connection_manager.connect(room_id, websocket)
    await chat_redis_bridge.register_room(room_id)

    try:
        while True:
            payload = await websocket.receive_json()
            content = payload.get("content") if isinstance(payload, dict) else None

            if not isinstance(content, str):
                await websocket.send_json({"type": "error", "detail": "Payload must include string field 'content'"})
                continue

            try:
                message = await create_ws_message(
                    conversation_id=room_id,
                    sender_id=str(UserId(str(current_user.id))),
                    content=content,
                )
            except ConversationNotFoundError as exc:
                await websocket.send_json({"type": "error", "detail": str(exc)})
                continue
            except MessageValidationError as exc:
                await websocket.send_json({"type": "error", "detail": str(exc)})
                continue
            except Exception:
                logger.exception("websocket_message_failed", conversation_id=room_id, user_id=str(current_user.id))
                raise

            outbound = ChatSocketMessageSchema(message=_message_to_response(message)).model_dump(mode="json")
            await chat_redis_bridge.fanout(room_id, outbound)
    except WebSocketDisconnect:
        pass
    finally:
        await chat_redis_bridge.unregister_room(room_id)
        await chat_connection_manager.disconnect(room_id, websocket)

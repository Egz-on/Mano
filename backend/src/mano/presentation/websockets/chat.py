"""WebSocket chat connection management."""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChatConnectionManager:
    """Tracks active websocket connections per conversation."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(conversation_id, []).append(websocket)

    async def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            room_connections = self._connections.get(conversation_id, [])
            if websocket in room_connections:
                room_connections.remove(websocket)
            if not room_connections and conversation_id in self._connections:
                self._connections.pop(conversation_id, None)

    async def broadcast(self, conversation_id: str, payload: dict[str, object]) -> None:
        async with self._lock:
            recipients = list(self._connections.get(conversation_id, []))

        stale_connections: list[WebSocket] = []
        for websocket in recipients:
            try:
                await websocket.send_json(payload)
            except Exception:  # pragma: no cover - defensive socket cleanup
                stale_connections.append(websocket)

        for websocket in stale_connections:
            await self.disconnect(conversation_id, websocket)


class RedisChatBridge:
    """Optional Redis fanout bridge for multi-instance websocket delivery."""

    def __init__(self, manager: ChatConnectionManager) -> None:
        self._manager = manager
        self._redis_client: object | None = None
        self._pubsub: object | None = None
        self._listener_task: asyncio.Task[None] | None = None
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    async def start(self, redis_client: object | None) -> None:
        if redis_client is None or not hasattr(redis_client, "pubsub") or not hasattr(redis_client, "publish"):
            self._active = False
            return
        if self._listener_task is not None:
            return

        self._redis_client = redis_client
        self._pubsub = redis_client.pubsub()
        await self._pubsub.psubscribe("chat:*")
        self._listener_task = asyncio.create_task(self._listen())
        self._active = True

    async def stop(self) -> None:
        self._active = False
        if self._listener_task is not None:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None
        if self._pubsub is not None:
            close = getattr(self._pubsub, "aclose", None)
            if callable(close):
                await close()
            self._pubsub = None

    async def fanout(self, conversation_id: str, payload: dict[str, object]) -> None:
        if self._active and self._redis_client is not None:
            try:
                envelope = dict(payload)
                envelope["conversation_id"] = conversation_id
                await self._redis_client.publish(f"chat:{conversation_id}", json.dumps(envelope))
                return
            except Exception as exc:  # pragma: no cover - optional infrastructure
                logger.warning("Redis chat publish failed: %s", exc)
        await self._manager.broadcast(conversation_id, payload)

    async def _listen(self) -> None:
        if self._pubsub is None:
            return

        try:
            while True:
                message = await self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message is None:
                    await asyncio.sleep(0.1)
                    continue

                data = message.get("data")
                if not isinstance(data, str):
                    continue

                payload = json.loads(data)
                conversation_id = payload.get("conversation_id")
                if isinstance(conversation_id, str):
                    payload.pop("conversation_id", None)
                    await self._manager.broadcast(conversation_id, payload)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - optional infrastructure
            logger.warning("Redis chat subscriber stopped unexpectedly: %s", exc)
            self._active = False


chat_connection_manager = ChatConnectionManager()
chat_redis_bridge = RedisChatBridge(chat_connection_manager)

"""Chat API schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationResponseSchema(BaseModel):
    """Conversation response payload."""

    id: UUID = Field(..., description="Conversation identifier")
    created_at: datetime = Field(..., description="Creation timestamp")


class ChatMessageCreateSchema(BaseModel):
    """HTTP and websocket message input payload."""

    content: str = Field(..., min_length=1, max_length=4000, description="Chat message body")


class ChatMessageResponseSchema(BaseModel):
    """Chat message response payload."""

    id: UUID = Field(..., description="Message identifier")
    conversation_id: UUID = Field(..., description="Parent conversation identifier")
    sender_id: UUID = Field(..., description="Sender identifier")
    content: str = Field(..., description="Normalized message body")
    created_at: datetime = Field(..., description="Creation timestamp")


class ChatSocketMessageSchema(BaseModel):
    """Outbound websocket message envelope."""

    type: str = Field(default="message", description="Socket event type")
    message: ChatMessageResponseSchema

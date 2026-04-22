"""Conversation domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import uuid


@dataclass(frozen=True)
class ConversationId:
    """Conversation identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Conversation:
    """Conversation aggregate root."""

    id: ConversationId
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls) -> "Conversation":
        return cls(id=ConversationId(), created_at=datetime.now(UTC))

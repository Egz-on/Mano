"""Email template domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmailTemplateId:
    """Email template ID value object."""

    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EmailTemplate:
    """Email template domain model."""

    id: EmailTemplateId
    name: str
    subject: str
    html_content: str
    text_content: str | None = None
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EmailTemplate:
        """Create EmailTemplate from dictionary."""
        return cls(
            id=EmailTemplateId(data["id"]),
            name=data["name"],
            subject=data["subject"],
            html_content=data["html_content"],
            text_content=data.get("text_content"),
            is_active=data.get("is_active", True),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id.value,
            "name": self.name,
            "subject": self.subject,
            "html_content": self.html_content,
            "text_content": self.text_content,
            "is_active": self.is_active,
        }

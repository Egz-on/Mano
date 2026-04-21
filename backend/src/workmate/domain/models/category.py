"""Category model"""

from __future__ import annotations

from datetime import datetime, UTC
import uuid
from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class CategoryId:
    """Category identifier value object."""

    value: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self) -> str:
        """Return string representation of CategoryId."""
        return self.value


@dataclass(frozen=True)
class Category:
    """Category domain entity."""

    id: CategoryId
    name: str
    slug: str
    icon: str | None
    description: str | None
    parent_id: CategoryId | None
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    def __str__(self) -> str:
        """Return string representation of Category."""
        return self.name

    def __repr__(self) -> str:
        """Return string representation of Category."""
        return f"Category(id={self.id}, name={self.name}, slug={self.slug}, icon={self.icon}, description={self.description}, parent_id={self.parent_id}, is_active={self.is_active}, display_order={self.display_order}, created_at={self.created_at}, updated_at={self.updated_at})"

    def active(self) -> Category:
        """Active the category."""
        return replace(self, is_active=True, updated_at=datetime.now())

    def deactive(self) -> Category:
        """Deactive the category."""
        return replace(self, is_active=False, updated_at=datetime.now())

    def update_description(self, new_description: str) -> Category:
        """Update the category description."""
        return replace(self, description=new_description, updated_at=datetime.now())

    def update_slug(self, new_slug: str) -> Category:
        """Update the category slug."""
        return replace(self, slug=new_slug, updated_at=datetime.now(UTC))

    def update_name(self, new_name: str) -> Category:
        """Update the category name."""
        return replace(self, name=new_name, updated_at=datetime.now())

    def update_icon(self, new_icon: str) -> Category:
        """Update the category icon."""
        return replace(self, icon=new_icon, updated_at=datetime.now())

    def update_parent_id(self, new_parent_id: CategoryId) -> Category:
        """Update the category parent id."""
        return replace(self, parent_id=new_parent_id, updated_at=datetime.now(UTC))

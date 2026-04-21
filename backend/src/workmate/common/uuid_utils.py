"""UUID conversion utilities for handling different UUID types safely."""

from __future__ import annotations

import uuid
from typing import Any


def uuid_to_str(uuid_obj: str | uuid.UUID | Any) -> str:  # noqa: PLR0911
    """Convert various UUID types to string safely using pattern matching.

    Handles:
    - Regular strings (pass-through)
    - Python UUID objects
    - Domain value objects with .value attribute (ItemId, SuggestionId, UserId)
    - PostgreSQL asyncpg UUID objects with .hex attribute
    - Any other object (fallback to str())

    Args:
        uuid_obj: The UUID object to convert to string

    Returns:
        String representation of the UUID
    """
    match uuid_obj:
        case str():
            return uuid_obj
        case uuid.UUID():
            return str(uuid_obj)
        case obj if hasattr(obj, "value"):
            # Handle domain value objects (ItemId, SuggestionId, UserId)
            inner_uuid = obj.value
            match inner_uuid:
                case str():
                    return inner_uuid
                case uuid.UUID():
                    return str(inner_uuid)
                case _:
                    return getattr(inner_uuid, "hex", str(inner_uuid))
        case obj if hasattr(obj, "hex"):
            # Handle PostgreSQL asyncpg UUID objects by accessing hex directly
            return str(obj.hex)
        case _:
            return str(uuid_obj)

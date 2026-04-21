"""Password hashing port."""

from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    """Abstraction for hashing and verifying passwords."""

    @abstractmethod
    def hash_password(self, raw_password: str) -> str:
        """Hash a raw password."""
        ...

    @abstractmethod
    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        """Verify a raw password against a hash."""
        ...

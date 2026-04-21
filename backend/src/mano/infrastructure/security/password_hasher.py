"""Password hashing implementation."""

from __future__ import annotations

import bcrypt

from mano.domain.repositories.password_hasher_port import PasswordHasherPort


class BcryptPasswordHasher(PasswordHasherPort):
    """BCrypt-based password hasher adapter."""

    def hash_password(self, raw_password: str) -> str:
        hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, raw_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), hashed_password.encode("utf-8"))

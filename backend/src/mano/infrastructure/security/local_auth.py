"""Local JWT auth utilities with hardcoded demo users."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TypedDict, cast
from uuid import NAMESPACE_DNS, uuid5

from jose import JWTError, jwt


class DemoUser(TypedDict):
    email: str
    password: str
    name: str
    surname: str
    role: str
    phone: str
    city: str | None
    auth_user_id: str


DEMO_USERS: dict[str, DemoUser] = {
    "admin@mano.com": {
        "email": "admin@mano.com",
        "password": "admin123",
        "name": "System",
        "surname": "Admin",
        "role": "admin",
        "phone": "+38970111222",
        "city": "Skopje",
        "auth_user_id": str(uuid5(NAMESPACE_DNS, "mano:admin@mano.com")),
    },
    "provider@mano.com": {
        "email": "provider@mano.com",
        "password": "provider123",
        "name": "Default",
        "surname": "Provider",
        "role": "provider",
        "phone": "+38970222333",
        "city": "Tetovo",
        "auth_user_id": "00000000-0000-0000-0000-000000000001",
    },
    "client@mano.com": {
        "email": "client@mano.com",
        "password": "client123",
        "name": "Guest",
        "surname": "Client",
        "role": "client",
        "phone": "+38970333444",
        "city": "Skopje",
        "auth_user_id": str(uuid5(NAMESPACE_DNS, "mano:client@mano.com")),
    },
}

ALGORITHM = "HS256"


def _split_name_parts(full_name: str) -> tuple[str, str]:
    normalized = " ".join(full_name.split())
    if not normalized:
        return "User", ""
    first_name, separator, remainder = normalized.partition(" ")
    return first_name, remainder if separator else ""


def authenticate_user(email: str, password: str) -> DemoUser | None:
    user = DEMO_USERS.get(email.strip().lower())
    if not user or user["password"] != password:
        return None
    return user


def create_access_token(
    *,
    secret_key: str,
    subject: str,
    role: str,
    name: str,
    surname: str,
    expires_minutes: int = 60 * 12,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role,
        "name": name,
        "surname": surname,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return cast(str, jwt.encode(payload, secret_key, algorithm=ALGORITHM))


def decode_access_token(token: str, *, secret_key: str) -> dict[str, str]:
    try:
        payload = cast(dict[str, object], jwt.decode(token, secret_key, algorithms=[ALGORITHM]))
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    sub = payload.get("sub")
    role = payload.get("role")
    name = payload.get("name")
    surname = payload.get("surname")
    if not isinstance(name, str):
        name, surname = _split_name_parts(str(payload.get("full_name", "User")))
    if not isinstance(sub, str) or not isinstance(role, str):
        raise ValueError("Invalid token payload")

    return {
        "sub": sub,
        "role": role,
        "name": name,
        "surname": surname if isinstance(surname, str) else "",
    }

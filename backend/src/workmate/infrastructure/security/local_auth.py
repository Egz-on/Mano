"""Local JWT auth utilities with hardcoded demo users."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TypedDict

from jose import JWTError, jwt


class DemoUser(TypedDict):
    email: str
    password: str
    full_name: str
    role: str
    phone: str
    city: str | None


DEMO_USERS: dict[str, DemoUser] = {
    "admin@workmate.com": {
        "email": "admin@workmate.com",
        "password": "admin123",
        "full_name": "System Admin",
        "role": "admin",
        "phone": "+38970111222",
        "city": "Skopje",
    },
    "provider@workmate.com": {
        "email": "provider@workmate.com",
        "password": "provider123",
        "full_name": "Default Provider",
        "role": "provider",
        "phone": "+38970222333",
        "city": "Tetovo",
    },
}

ALGORITHM = "HS256"


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
    full_name: str,
    expires_minutes: int = 60 * 12,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role,
        "full_name": full_name,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, *, secret_key: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    sub = payload.get("sub")
    role = payload.get("role")
    full_name = payload.get("full_name")
    if not isinstance(sub, str) or not isinstance(role, str):
        raise ValueError("Invalid token payload")

    return {"sub": sub, "role": role, "full_name": full_name if isinstance(full_name, str) else "User"}

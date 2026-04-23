import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mano.dependencies import get_email_sender
from mano.domain.repositories.email_sender_port import EmailSenderPort
from mano.infrastructure.database.models import Base  # Exception: needed for table creation
from mano.infrastructure.database.connection import get_db_session
from mano.main import app
from mano.infrastructure.cache.connection import get_redis_client
from mano.infrastructure.config.settings import get_settings
from mano.infrastructure.security.local_auth import create_access_token


class FakeRedis:
    async def get(self, key: str) -> str | None:
        return None

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        _ = (key, value, ex)
        return True

    async def delete(self, key: str) -> int:
        return 1

    async def aclose(self) -> None:
        return None


class FakeEmailSender(EmailSenderPort):
    def __init__(self) -> None:
        self.sent_messages: list[dict[str, str | None]] = []

    async def send_email(
        self,
        *,
        recipient: str,
        subject: str,
        text_body: str,
        html_body: str | None = None,
    ) -> None:
        self.sent_messages.append(
            {
                "recipient": recipient,
                "subject": subject,
                "text_body": text_body,
                "html_body": html_body,
            }
        )


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    test_database_path = Path("/tmp") / f"mano-test-{uuid4().hex}.sqlite"
    test_database_url = f"sqlite+aiosqlite:///{test_database_path}"
    sync_test_database_url = f"sqlite:///{test_database_path}"
    engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )
    sync_engine: Engine = create_engine(
        sync_test_database_url,
        connect_args={"check_same_thread": False},
    )
    testing_session_local = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        Base.metadata.create_all(sync_engine)

        async with testing_session_local() as session:
            yield session
            await session.close()
    finally:
        await engine.dispose()
        sync_engine.dispose()
        if test_database_path.exists():
            test_database_path.unlink()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    email_sender = FakeEmailSender()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession]:
        yield db_session

    async def override_get_redis_client() -> AsyncGenerator[FakeRedis]:
        client = FakeRedis()
        yield client

    def override_get_email_sender() -> EmailSenderPort:
        return email_sender

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_redis_client] = override_get_redis_client
    app.dependency_overrides[get_email_sender] = override_get_email_sender

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


def _build_auth_header(*, email: str, role: str, name: str, surname: str) -> dict[str, str]:
    secret_key = get_settings().secret_key or "dev-secret-change-me"
    token = create_access_token(
        secret_key=secret_key,
        subject=email,
        role=role,
        name=name,
        surname=surname,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_header_admin() -> dict[str, str]:
    return _build_auth_header(email="admin@mano.com", role="admin", name="System", surname="Admin")


@pytest.fixture
def auth_header_provider() -> dict[str, str]:
    return _build_auth_header(email="provider@mano.com", role="provider", name="Default", surname="Provider")


@pytest.fixture
def auth_header_client() -> dict[str, str]:
    return _build_auth_header(email="client@mano.com", role="client", name="Guest", surname="Client")

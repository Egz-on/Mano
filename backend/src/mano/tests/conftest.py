import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from mano.dependencies import get_email_sender
from mano.domain.repositories.email_sender_port import EmailSenderPort
from mano.infrastructure.database.models import Base  # Exception: needed for table creation
from mano.infrastructure.database.connection import get_db_session
from mano.main import app
from mano.infrastructure.cache.connection import get_redis_client
from mano.infrastructure.config.settings import get_settings
from mano.infrastructure.security.local_auth import create_access_token

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


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
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    # Drop tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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

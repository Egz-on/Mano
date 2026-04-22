"""Database connection setup."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from mano.infrastructure.config.settings import get_settings


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str | None = None) -> None:
        settings = get_settings()
        self._database_url = database_url or settings.database.url
        self._engine = create_async_engine(
            self._database_url,
            echo=settings.debug,
            future=True,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """Get database session."""
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Return the configured async session factory."""
        return self._session_factory

    async def close(self) -> None:
        """Close database connection."""
        await self._engine.dispose()


# Global database instance
database = Database()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency for getting database session."""
    async for session in database.get_session():
        yield session

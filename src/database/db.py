import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from src.conf.config import settings


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Async context manager for database session management.

        Ensures that a new session is created and provided for the
        duration of the context manager. Handles session rollback
        in case of an exception and ensures the session is closed
        after use.

        Yields:
            AsyncSession: The database session.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If an error occurs during the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    FastAPI dependency for database session management.

    This is a dependency that can be injected into FastAPI path
    operations to provide a database session. It is an async
    generator that will yield a database session object within
    the context of the async context manager.

    The session is rolled back and closed when the context
    manager exits.

    Yields:
        AsyncSession: The database session.
    """
    async with sessionmanager.session() as session:
        yield session

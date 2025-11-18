from __future__ import annotations

from collections.abc import AsyncIterator
import os
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

DEFAULT_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"

engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def configure_engine(database_url: str | None = None) -> None:
    """Configure the async engine and session factory.

    The database URL can be supplied directly or via the ``DATABASE_URL`` environment
    variable. When not provided, the application defaults to the Postgres service
    defined in ``docker-compose.yml``.
    """

    global engine, AsyncSessionLocal

    url = database_url or os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    engine = create_async_engine(url, echo=False, future=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def _ensure_engine() -> None:
    if engine is None or AsyncSessionLocal is None:
        configure_engine()


async def get_session() -> AsyncIterator[AsyncSession]:
    _ensure_engine()
    assert AsyncSessionLocal is not None  # for type-checkers

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------
# Database URL
# ------------------------------------------------------------------

DATABASE_URL = os.getenv("POSTGRES_URI")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set")


# ------------------------------------------------------------------
# Async Engine
# ------------------------------------------------------------------

engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # SQL logs (disable in prod)
    pool_pre_ping=True, # Detect stale connections
)


# ------------------------------------------------------------------
# Async Session Factory
# ------------------------------------------------------------------

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------
# Dependency / Context Manager
# ------------------------------------------------------------------

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI-compatible async DB session generator.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

import uuid
from typing import Optional
from datetime import datetime
from uuid import UUID as PythonUUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Text, DateTime

from db.session import engine
from db.base import Base


def _serialize_state(state: dict) -> dict:
    """Convert datetime and UUID objects to ISO/string format for JSON serialization."""
    def convert_value(v):
        if isinstance(v, datetime):
            return v.isoformat()
        elif isinstance(v, PythonUUID):
            return str(v)
        elif isinstance(v, dict):
            return {k: convert_value(val) for k, val in v.items()}
        elif isinstance(v, (list, tuple)):
            return [convert_value(item) for item in v]
        return v
    
    return convert_value(state)


# -------------------------------------------------
# Table definition (SQLAlchemy Core)
# -------------------------------------------------

agent_sessions = Table(
    "agent_sessions",
    Base.metadata,
    Column("session_id", UUID(as_uuid=True), primary_key=True),
    Column("agent_name", Text, nullable=False),
    Column("state", JSONB, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), onupdate=func.now()),
)


# -------------------------------------------------
# Service
# -------------------------------------------------

class AgentSessionService:

    @staticmethod
    async def create(
        db: AsyncSession,
        agent_name: str,
        state: dict,
    ) -> uuid.UUID:
        session_id = uuid.uuid4()

        stmt = insert(agent_sessions).values(
            session_id=session_id,
            agent_name=agent_name,
            state=_serialize_state(state),
        )
        await db.execute(stmt)
        await db.commit()

        return session_id

    @staticmethod
    async def get(
        db: AsyncSession,
        session_id: uuid.UUID,
    ) -> Optional[dict]:
        stmt = select(agent_sessions.c.state).where(
            agent_sessions.c.session_id == session_id
        )
        result = await db.execute(stmt)
        row = result.first()
        return row[0] if row else None

    @staticmethod
    async def update(
        db: AsyncSession,
        session_id: uuid.UUID,
        state: dict,
    ) -> None:
        stmt = (
            update(agent_sessions)
            .where(agent_sessions.c.session_id == session_id)
            .values(
                state=_serialize_state(state),
                updated_at=func.now(),
            )
        )
        await db.execute(stmt)
        await db.commit()

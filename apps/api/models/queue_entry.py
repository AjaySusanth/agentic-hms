from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class QueueEntry(Base):
    __tablename__ = "queue_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    queue_id = Column(
        UUID(as_uuid=True),
        ForeignKey("doctor_queues.id", ondelete="CASCADE"),
        nullable=False,
    )

    visit_id = Column(UUID(as_uuid=True), nullable=False)

    token_number = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)

    status = Column(
        Text,
        nullable=False,
    )

    check_in_time = Column(DateTime(timezone=True))
    consultation_start_time = Column(DateTime(timezone=True))
    consultation_end_time = Column(DateTime(timezone=True))

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    queue = relationship("DoctorQueue", back_populates="entries")

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Time,
    Boolean,
    Integer,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from db.base import Base


class DoctorQueue(Base):
    __tablename__ = "doctor_queues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    doctor_id = Column(UUID(as_uuid=True), nullable=False)
    hospital_id = Column(UUID(as_uuid=True), nullable=False)
    queue_date = Column(Date, nullable=False)

    shift_start_time = Column(Time, nullable=False)
    shift_end_time = Column(Time, nullable=False)

    queue_open = Column(Boolean, default=True)
    max_queue_size = Column(Integer)
    avg_consult_time_minutes = Column(Integer, default=10)

    current_token = Column(Integer, default=0)
    current_visit_id = Column(UUID(as_uuid=True))

    last_event_type = Column(Text)
    last_event_reason = Column(Text)
    last_updated_by = Column(Text)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    entries = relationship(
        "QueueEntry",
        back_populates="queue",
        cascade="all, delete-orphan",
    )

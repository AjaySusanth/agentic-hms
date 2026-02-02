from sqlalchemy import Column, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from db.base import Base


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False)

    medicine_name = Column(Text, nullable=False)
    dosage = Column(Text)
    frequency = Column(Text)
    duration_days = Column(Integer)
    instructions = Column(Text)

    availability_status = Column(Text, default="unknown")  # future use

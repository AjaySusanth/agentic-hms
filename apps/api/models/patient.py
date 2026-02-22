from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from db.base import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    hospital_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    contact_number: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    abha_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    visits = relationship("Visit", back_populates="patient")

    __table_args__ = (
        UniqueConstraint("contact_number", "hospital_id", name="uq_patient_phone_hospital"),
        UniqueConstraint("abha_id", "hospital_id", name="uq_patient_abha_hospital"),
    )

    def __repr__(self) -> str:
        return f"<Patient(name={self.full_name}, phone={self.contact_number})>"

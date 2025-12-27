from sqlalchemy import String, Integer, DateTime
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
        unique=True,
        nullable=False,
    )

    abha_id: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    visits = relationship("Visit", back_populates="patient")

    def __repr__(self) -> str:
        return f"<Patient(name={self.full_name}, phone={self.contact_number})>"

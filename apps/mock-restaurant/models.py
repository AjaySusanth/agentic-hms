"""
SQLAlchemy models for the mock restaurant backend.
Completely independent from the HMS platform.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(String, unique=True, nullable=False)  # "T1", "T2"
    capacity = Column(Integer, nullable=False)                  # 2, 4, 6, 8
    location = Column(String, nullable=False)                   # "indoor", "outdoor", "private"
    description = Column(String, default="")

    reservations = relationship("Reservation", back_populates="table")

    def to_dict(self):
        return {
            "id": self.id,
            "table_number": self.table_number,
            "capacity": self.capacity,
            "location": self.location,
            "description": self.description,
        }


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    guest_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    date = Column(String, nullable=False)      # "2026-03-10"
    time = Column(String, nullable=False)      # "19:00"
    party_size = Column(Integer, nullable=False)
    status = Column(String, default="confirmed")  # "confirmed", "cancelled"
    created_at = Column(DateTime, default=datetime.utcnow)

    table = relationship("Table", back_populates="reservations")

    def to_dict(self):
        return {
            "id": self.id,
            "table_id": self.table_id,
            "table_number": self.table.table_number if self.table else None,
            "guest_name": self.guest_name,
            "phone": self.phone,
            "date": self.date,
            "time": self.time,
            "party_size": self.party_size,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

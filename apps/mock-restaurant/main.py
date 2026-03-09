"""
Mock Restaurant Backend — Standalone FastAPI app.
Simulates an external restaurant's reservation API.
Runs on port 8001, completely independent from the HMS platform.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Table, Reservation
from seed_data import seed_database


# ── Database Setup (SQLite, in-memory for demo) ─────────────────
engine = create_engine("sqlite:///restaurant.db", echo=False)
SessionLocal = sessionmaker(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed on startup."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)
    yield


app = FastAPI(
    title="Mock Restaurant API",
    description="Simulates a restaurant reservation system for template demo",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Pydantic Schemas ────────────────────────────────────────────
class ReservationRequest(BaseModel):
    guest_name: str
    phone: str
    date: str           # "2026-03-10"
    time: str           # "19:00"
    party_size: int
    table_id: int


class ReservationResponse(BaseModel):
    id: str
    table_id: int
    table_number: Optional[str] = None
    guest_name: str
    phone: str
    date: str
    time: str
    party_size: int
    status: str
    created_at: Optional[str] = None


# ── Endpoints ───────────────────────────────────────────────────

@app.get("/api/tables/available")
def search_available_tables(
    date: str = Query(..., description="Reservation date, e.g. 2026-03-10"),
    time: str = Query(..., description="Reservation time, e.g. 19:00"),
    party_size: int = Query(..., description="Number of guests"),
):
    """
    Find tables that can seat the party and have no conflicting reservation.
    """
    with SessionLocal() as session:
        # Get all tables that can fit the party
        all_tables = (
            session.query(Table)
            .filter(Table.capacity >= party_size)
            .order_by(Table.capacity)
            .all()
        )

        # Find tables already reserved for this date+time
        reserved_table_ids = {
            r.table_id
            for r in session.query(Reservation)
            .filter(
                Reservation.date == date,
                Reservation.time == time,
                Reservation.status == "confirmed",
            )
            .all()
        }

        # Return only available tables
        available = [t.to_dict() for t in all_tables if t.id not in reserved_table_ids]

    if not available:
        return {"tables": [], "message": "No tables available for the selected date, time, and party size."}

    return {"tables": available, "count": len(available)}


@app.post("/api/reservations", response_model=ReservationResponse)
def create_reservation(req: ReservationRequest):
    """Create a new reservation."""
    with SessionLocal() as session:
        # Verify the table exists
        table = session.query(Table).filter(Table.id == req.table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail=f"Table with id {req.table_id} not found")

        # Check capacity
        if req.party_size > table.capacity:
            raise HTTPException(
                status_code=400,
                detail=f"Table {table.table_number} seats {table.capacity}, but party size is {req.party_size}",
            )

        # Check if already reserved
        existing = (
            session.query(Reservation)
            .filter(
                Reservation.table_id == req.table_id,
                Reservation.date == req.date,
                Reservation.time == req.time,
                Reservation.status == "confirmed",
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Table {table.table_number} is already reserved for {req.date} at {req.time}",
            )

        reservation = Reservation(
            table_id=req.table_id,
            guest_name=req.guest_name,
            phone=req.phone,
            date=req.date,
            time=req.time,
            party_size=req.party_size,
            status="confirmed",
        )
        session.add(reservation)
        session.commit()
        session.refresh(reservation)

        return ReservationResponse(
            id=reservation.id,
            table_id=reservation.table_id,
            table_number=table.table_number,
            guest_name=reservation.guest_name,
            phone=reservation.phone,
            date=reservation.date,
            time=reservation.time,
            party_size=reservation.party_size,
            status=reservation.status,
            created_at=reservation.created_at.isoformat() if reservation.created_at else None,
        )


@app.get("/api/reservations/{reservation_id}", response_model=ReservationResponse)
def get_reservation(reservation_id: str):
    """Look up a reservation by ID."""
    with SessionLocal() as session:
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        return ReservationResponse(
            id=reservation.id,
            table_id=reservation.table_id,
            table_number=reservation.table.table_number if reservation.table else None,
            guest_name=reservation.guest_name,
            phone=reservation.phone,
            date=reservation.date,
            time=reservation.time,
            party_size=reservation.party_size,
            status=reservation.status,
            created_at=reservation.created_at.isoformat() if reservation.created_at else None,
        )


@app.delete("/api/reservations/{reservation_id}")
def cancel_reservation(reservation_id: str):
    """Cancel a reservation."""
    with SessionLocal() as session:
        reservation = session.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=404, detail="Reservation not found")

        if reservation.status == "cancelled":
            raise HTTPException(status_code=400, detail="Reservation is already cancelled")

        reservation.status = "cancelled"
        session.commit()

        return {
            "message": "Reservation cancelled successfully",
            "reservation_id": reservation_id,
            "status": "cancelled",
        }


# ── Health Check ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "Mock Restaurant API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

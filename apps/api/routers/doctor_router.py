from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from db.session import get_db_session
from models.doctor import Doctor
from models.department import Department

router = APIRouter(prefix="/doctors", tags=["Doctors"])


class DoctorLoginRequest(BaseModel):
    name: str  # Simplified login - just using name for MVP


class DoctorLoginResponse(BaseModel):
    doctor_id: UUID
    name: str
    specialization: Optional[str]
    department_name: Optional[str]
    is_available: bool


@router.post("/login", response_model=DoctorLoginResponse)
async def doctor_login(
    request: DoctorLoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Minimal doctor login - finds doctor by name (MVP approach)
    In production, this would use proper authentication
    """
    try:
        # Find doctor by name (case-insensitive partial match)
        result = await db.execute(
            select(Doctor)
            .where(Doctor.name.ilike(f"%{request.name}%"))
            .limit(1)
        )
        doctor = result.scalar_one_or_none()

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail=f"No doctor found with name containing '{request.name}'"
            )

        # Get department name
        department_name = None
        if doctor.department_id:
            dept = await db.get(Department, doctor.department_id)
            if dept:
                department_name = dept.name

        return DoctorLoginResponse(
            doctor_id=doctor.id,
            name=doctor.name,
            specialization=doctor.specialization,
            department_name=department_name,
            is_available=doctor.is_available,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doctor_id}", response_model=DoctorLoginResponse)
async def get_doctor(
    doctor_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Get doctor details by ID"""
    try:
        doctor = await db.get(Doctor, doctor_id)
        
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # Get department name
        department_name = None
        if doctor.department_id:
            dept = await db.get(Department, doctor.department_id)
            if dept:
                department_name = dept.name

        return DoctorLoginResponse(
            doctor_id=doctor.id,
            name=doctor.name,
            specialization=doctor.specialization,
            department_name=department_name,
            is_available=doctor.is_available,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

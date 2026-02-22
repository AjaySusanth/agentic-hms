from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.hospital_service import HospitalService
from db.session import get_db_session
from models.hospital import Hospital
from typing import List
import uuid
from schemas.hospital import HospitalOut, HospitalCreate

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.post("", response_model=HospitalOut)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: AsyncSession = Depends(get_db_session),
):
    service = HospitalService(db)
    return await service.create(
        name=hospital_data.name,
        code=hospital_data.code,
        location=hospital_data.location,
        address=hospital_data.address,
        contact_number=hospital_data.contact_number,
    )


@router.get("", response_model=List[HospitalOut])
async def list_hospitals(db: AsyncSession = Depends(get_db_session)):
    service = HospitalService(db)
    return await service.list_all()


@router.get("/search", response_model=List[HospitalOut])
async def search_hospitals(
    department: str = None, location: str = None, db: AsyncSession = Depends(get_db_session)
):
    service = HospitalService(db)
    if department:
        return await service.search_by_department(department)
    if location:
        return await service.search_by_location(location)
    return await service.list_all()


@router.get("/{hospital_id}", response_model=HospitalOut)
async def get_hospital(hospital_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)):
    service = HospitalService(db)
    hospital = await service.get_by_id(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

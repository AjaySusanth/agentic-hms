from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.doctor import Doctor
from models.department import Department

from typing import Optional

class DoctorService:

    @staticmethod
    async def list_available_by_department(
        db: AsyncSession,
        department_id,
        hospital_id: Optional[str] = None,
    ) -> List[Doctor]:
        stmt = (
            select(Doctor)
            .join(Department)
            .where(
                Department.id == department_id,
                Doctor.is_available.is_(True),
            )
            .order_by(Doctor.name)
        )
        if hospital_id:
            stmt = stmt.where(Doctor.hospital_id == hospital_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        doctor_id,
    ) -> Doctor | None:
        stmt = select(Doctor).where(Doctor.id == doctor_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

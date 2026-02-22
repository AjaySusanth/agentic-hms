from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.department import Department
from typing import Optional

class DepartmentService:

    @staticmethod
    async def list_all(
        db: AsyncSession, hospital_id: Optional[str] = None
    ) -> List[Department]:
        stmt = select(Department).order_by(Department.name)
        if hospital_id:
            stmt = stmt.where(Department.hospital_id == hospital_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str,
        hospital_id: Optional[str] = None,
    ) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        if hospital_id:
            stmt = stmt.where(Department.hospital_id == hospital_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

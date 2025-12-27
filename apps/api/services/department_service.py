from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.department import Department


class DepartmentService:

    @staticmethod
    async def list_all(db: AsyncSession) -> List[Department]:
        stmt = select(Department).order_by(Department.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_by_name(
        db: AsyncSession,
        name: str,
    ) -> Department | None:
        stmt = select(Department).where(Department.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

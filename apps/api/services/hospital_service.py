from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.hospital import Hospital
from typing import List, Optional
import uuid


class HospitalService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, name: str, code: str, location: str, address: str, contact_number: str
    ) -> Hospital:
        hospital = Hospital(
            id=uuid.uuid4(),
            name=name,
            code=code,
            location=location,
            address=address,
            contact_number=contact_number,
            is_active=True,
        )
        self.db.add(hospital)
        await self.db.commit()
        await self.db.refresh(hospital)
        return hospital

    async def list_all(self) -> List[Hospital]:
        result = await self.db.execute(select(Hospital))
        return result.scalars().all()

    async def search_by_department(self, department_name: str) -> List[Hospital]:
        from models.department import Department
        
        # Subquery to get hospital_ids for the department
        subquery = (
            select(Department.hospital_id)
            .filter(Department.name == department_name)
            .distinct()
        )
        
        result = await self.db.execute(
            select(Hospital).where(Hospital.id.in_(subquery))
        )
        return result.scalars().all()

    async def search_by_location(self, location: str) -> List[Hospital]:
        result = await self.db.execute(
            select(Hospital).filter(Hospital.location.ilike(f"%{location}%"))
        )
        return result.scalars().all()

    async def get_by_id(self, hospital_id: uuid.UUID) -> Optional[Hospital]:
        return await self.db.get(Hospital, hospital_id)

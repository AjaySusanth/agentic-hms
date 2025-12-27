from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.patient import Patient


class PatientService:

    @staticmethod
    async def get_by_phone(
        db: AsyncSession,
        phone_number: str,
    ) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.contact_number == phone_number)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        full_name: str,
        age: int,
        contact_number: str,
        abha_id: Optional[str] = None,
    ) -> Patient:
        patient = Patient(
            full_name=full_name,
            age=age,
            contact_number=contact_number,
            abha_id=abha_id,
        )

        db.add(patient)
        await db.commit()
        await db.refresh(patient)

        return patient

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from models.prescription import Prescription
from models.prescription_item import PrescriptionItem


class PrescriptionService:

    @staticmethod
    async def get_or_create_prescription(
        db: AsyncSession,
        *,
        visit_id: UUID,
    ) -> Prescription:
        result = await db.execute(
            select(Prescription).where(Prescription.visit_id == visit_id)
        )
        prescription = result.scalar_one_or_none()

        if not prescription:
            prescription = Prescription(visit_id=visit_id)
            db.add(prescription)
            await db.flush()

        return prescription

    @staticmethod
    async def add_item(
        db: AsyncSession,
        *,
        visit_id: UUID,
        medicine_name: str,
        dosage: str | None,
        frequency: str | None,
        duration_days: int | None,
        instructions: str | None,
    ) -> PrescriptionItem:

        prescription = await PrescriptionService.get_or_create_prescription(
            db,
            visit_id=visit_id,
        )

        item = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_name=medicine_name,
            dosage=dosage,
            frequency=frequency,
            duration_days=duration_days,
            instructions=instructions,
        )

        db.add(item)
        await db.commit()
        await db.refresh(item)

        return item

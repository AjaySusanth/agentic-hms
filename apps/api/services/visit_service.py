from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from models.visit import Visit


class VisitService:

    @staticmethod
    async def create(
        db: AsyncSession,
        *,
        patient_id: UUID,
        doctor_id: UUID,
        symptoms_summary: str | None,
    ) -> Visit:
        """
        Creates a visit for a patient with a doctor.
        """
        visit = Visit(
            patient_id=patient_id,
            doctor_id=doctor_id,
            symptoms_summary=symptoms_summary,
            status="scheduled",
        )

        db.add(visit)
        await db.commit()
        await db.refresh(visit)

        return visit

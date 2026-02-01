from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from models.consultation import Consultation


class ConsultationService:

    @staticmethod
    async def upsert_notes(
        db: AsyncSession,
        *,
        visit_id: UUID,
        doctor_id: UUID,
        patient_id: UUID,
        notes: str,
        started_at: datetime,
    ) -> Consultation:
        """
        Create or update consultation notes for a visit.
        """
        result = await db.execute(
            select(Consultation).where(Consultation.visit_id == visit_id)
        )
        consultation = result.scalar_one_or_none()

        if consultation:
            consultation.notes = notes
            consultation.updated_at = datetime.utcnow()
        else:
            consultation = Consultation(
                visit_id=visit_id,
                doctor_id=doctor_id,
                patient_id=patient_id,
                notes=notes,
                started_at=started_at,
            )
            db.add(consultation)

        await db.commit()
        await db.refresh(consultation)
        return consultation

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date
from uuid import UUID

from models.visit import Visit
from models.doctor import Doctor


class VisitService:

    @staticmethod
    async def create_with_token(
        db: AsyncSession,
        *,
        patient_id: UUID,
        doctor_id: UUID,
        symptoms_summary: str | None,
    ) -> Visit:
        """
        Creates a visit and assigns the next token number
        per doctor per day (atomic).
        """

        # Get today's max token for this doctor
        stmt = (
            select(func.max(Visit.token_number))
            .where(
                Visit.doctor_id == doctor_id,
                func.date(Visit.created_at) == date.today(),
            )
        )

        result = await db.execute(stmt)
        max_token = result.scalar() or 0
        next_token = max_token + 1

        visit = Visit(
            patient_id=patient_id,
            doctor_id=doctor_id,
            symptoms_summary=symptoms_summary,
            token_number=next_token,
            status="scheduled",
        )

        db.add(visit)
        await db.commit()
        await db.refresh(visit)

        return visit

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from agents.queue.schemas import QueueIntakeRequest, QueueIntakeResponse
from models.doctor_queue import DoctorQueue
from models.queue_entry import QueueEntry
from models.visit import Visit


class QueueIntakeService:

    @staticmethod
    async def intake(
        db: AsyncSession,
        request: QueueIntakeRequest,
    ) -> QueueIntakeResponse:

        async with db.begin():  # 🔒 TRANSACTION START

            # 1️⃣ Get or create doctor queue
            result = await db.execute(
                select(DoctorQueue).where(
                    DoctorQueue.doctor_id == request.doctor_id,
                    DoctorQueue.queue_date == request.queue_date,
                )
            )
            queue = result.scalar_one_or_none()

            if not queue:
                # MVP: hardcoded shift (can later move to doctor table)
                queue = DoctorQueue(
                    doctor_id=request.doctor_id,
                    queue_date=request.queue_date,
                    shift_start_time=datetime.strptime("09:00", "%H:%M").time(),
                    shift_end_time=datetime.strptime("17:00", "%H:%M").time(),
                    avg_consult_time_minutes=10,
                    queue_open=True,
                )
                db.add(queue)
                await db.flush()

            # 2️⃣ Queue open check
            if not queue.queue_open:
                return QueueIntakeResponse(
                    accepted=False,
                    reason="Doctor queue is closed for today",
                )

            # 3️⃣ Active queue size
            result = await db.execute(
                select(func.count(QueueEntry.id)).where(
                    QueueEntry.queue_id == queue.id,
                    QueueEntry.status.in_(["waiting", "present", "in_consultation"]),
                )
            )
            active_count = result.scalar() or 0

            # 4️⃣ Expected finish time
            expected_finish = (
                datetime.combine(queue.queue_date, queue.shift_start_time)
                + timedelta(minutes=(active_count + 1) * queue.avg_consult_time_minutes)
            )

            shift_end = datetime.combine(
                queue.queue_date, queue.shift_end_time
            )

            if expected_finish > shift_end:
                queue.queue_open = False
                return QueueIntakeResponse(
                    accepted=False,
                    reason="Doctor shift will end before consultation",
                )

            # 5️⃣ Assign token
            token_number = active_count + 1

            entry = QueueEntry(
                queue_id=queue.id,
                visit_id=request.visit_id,
                token_number=token_number,
                position=token_number,
                status="waiting",
            )
            db.add(entry)

            # 6️⃣ Update visit
            visit = await db.get(Visit, request.visit_id)
            visit.token_number = token_number

            queue.last_event_type = "VISIT_ADDED"
            queue.last_event_reason = "Within shift capacity"
            queue.last_updated_by = "queue_agent"

        # 🔓 TRANSACTION COMMIT

        return QueueIntakeResponse(
            accepted=True,
            token_number=token_number,
            position=token_number,
            estimated_wait_minutes=active_count * queue.avg_consult_time_minutes,
        )

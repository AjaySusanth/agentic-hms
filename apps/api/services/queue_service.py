from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,asc
from datetime import datetime, timedelta

from agents.queue.schemas import QueueIntakeRequest, QueueIntakeResponse,CallNextResponse,CallNextRequest,EndConsultationResponse,EndConsultationRequest
from models.doctor_queue import DoctorQueue
from models.queue_entry import QueueEntry
from models.visit import Visit
from models.patient import Patient
from models.doctor import Doctor
from models.department import Department
from agents.doctor_assistance.agent import DoctorAssistanceAgent
from agents.doctor_assistance.state import DoctorAssistanceState


class QueueService:

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
    
    @staticmethod
    async def call_next(
        db: AsyncSession,
        request: CallNextRequest,
    ) -> CallNextResponse:

        async with db.begin():

            # 0️⃣ Validate doctor exists
            doctor = await db.get(Doctor, request.doctor_id)
            if not doctor:
                raise ValueError("Doctor not found")

            # 1️⃣ Fetch queue
            result = await db.execute(
                select(DoctorQueue).where(
                    DoctorQueue.doctor_id == request.doctor_id,
                    DoctorQueue.queue_date == request.queue_date,
                )
            )
            queue = result.scalar_one_or_none()

            if not queue:
                raise ValueError("No active queue for this doctor")

            if queue.current_visit_id:
                raise ValueError("Consultation already in progress")

            # 2️⃣ Pick next entry (present > waiting)
            result = await db.execute(
                select(QueueEntry)
                .where(
                    QueueEntry.queue_id == queue.id,
                    QueueEntry.status.in_(["present", "waiting"]),
                )
                .order_by(
                    asc(
                        QueueEntry.status != "present"
                    ),  # present first
                    asc(QueueEntry.token_number),
                )
                .limit(1)
            )

            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError("No patients waiting in queue")

            # 3️⃣ Mark entry as in consultation
            entry.status = "in_consultation"
            entry.consultation_start_time = datetime.utcnow()

            # 4️⃣ Update queue
            queue.current_token = entry.token_number
            queue.current_visit_id = entry.visit_id
            queue.last_event_type = "CALL_NEXT"
            queue.last_event_reason = "Doctor called next patient"
            queue.last_updated_by = "doctor"

            # 5️⃣ Fetch visit + patient context
            visit = await db.get(Visit, entry.visit_id)
            patient = await db.get(Patient, visit.patient_id)
            doctor = await db.get(Doctor, visit.doctor_id)
            # Eagerly resolve department name to avoid async lazy-load later
            if not doctor:
                raise ValueError("Doctor not found for visit")
            dept_name = None
            if doctor.department_id:
                dept = await db.get(Department, doctor.department_id)
                if not dept:
                    raise ValueError("Doctor department not found")
                dept_name = dept.name
        # 🔓 COMMIT DONE — SAFE TO HANDOFF

        # 6️⃣ Handoff to Doctor Assistance Agent
        state = DoctorAssistanceState(
            visit_id=visit.id,
            patient_id=patient.id,
            doctor_id=visit.doctor_id,
            department=dept_name,
            token_number=entry.token_number,
            symptoms_summary=visit.symptoms_summary,
        )

        DoctorAssistanceAgent(state).handle()

        return CallNextResponse(
            visit_id=visit.id,
            patient_id=patient.id,
            doctor_id=visit.doctor_id,
            token_number=entry.token_number,
            status="in_consultation",
        )

    @staticmethod
    async def end_consultation(
        db: AsyncSession,
        request: EndConsultationRequest,
    ) -> EndConsultationResponse:

        async with db.begin():  # 🔒 TRANSACTION START

            # 1️⃣ Fetch doctor queue
            result = await db.execute(
                select(DoctorQueue).where(
                    DoctorQueue.doctor_id == request.doctor_id,
                    DoctorQueue.queue_date == request.queue_date,
                )
            )
            queue = result.scalar_one_or_none()

            if not queue or not queue.current_visit_id:
                raise ValueError("No active consultation for this doctor")

            # 2️⃣ Validate visit
            if queue.current_visit_id != request.visit_id:
                raise ValueError("Visit does not match active consultation")

            # 3️⃣ Fetch queue entry
            result = await db.execute(
                select(QueueEntry).where(
                    QueueEntry.queue_id == queue.id,
                    QueueEntry.visit_id == request.visit_id,
                    QueueEntry.status == "in_consultation",
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError("Queue entry not found or already closed")

            # 4️⃣ Close queue entry
            entry.status = "completed"
            entry.consultation_end_time = datetime.utcnow()

            # 5️⃣ Update visit
            visit = await db.get(Visit, request.visit_id)
            visit.status = "completed"

            # 6️⃣ Free doctor queue
            queue.current_visit_id = None
            queue.current_token = None
            queue.last_event_type = "CONSULTATION_ENDED"
            queue.last_event_reason = "Doctor ended consultation"
            queue.last_updated_by = "doctor"

        # 🔓 TRANSACTION COMMIT

        return EndConsultationResponse(
            success=True,
            visit_id=request.visit_id,
            message="Consultation ended successfully",
        )
    
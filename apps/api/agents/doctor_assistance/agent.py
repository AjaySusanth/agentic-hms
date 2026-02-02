from typing import Dict, Any
from datetime import datetime, date
import os

from agents.base.agent import BaseAgent
from agents.doctor_assistance.state import (
    DoctorAssistanceState,
    DoctorAssistanceStep,
)
from agents.doctor_assistance.queue_client import QueueAgentClient
from services.consultation_service import ConsultationService
from services.prescription_service import PrescriptionService

QUEUE_AGENT_BASE_URL = os.getenv("QUEUE_AGENT_BASE_URL", "http://localhost:8000")


class DoctorAssistanceAgent(BaseAgent[DoctorAssistanceState]):

    allowed_transitions = {
        DoctorAssistanceStep.IDLE: [DoctorAssistanceStep.READY],
        DoctorAssistanceStep.READY: [DoctorAssistanceStep.IN_CONSULTATION],
        DoctorAssistanceStep.IN_CONSULTATION: [DoctorAssistanceStep.COMPLETED],
    }

    def __init__(self, state: DoctorAssistanceState, db=None):
        super().__init__(state)
        self.queue_client = QueueAgentClient(base_url=QUEUE_AGENT_BASE_URL)
        self.db = db

    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        step = self.state.step

        if step == DoctorAssistanceStep.IDLE:
            return await self._handle_idle(input_data)

        if step == DoctorAssistanceStep.READY:
            return await self._handle_ready(input_data)

        if step == DoctorAssistanceStep.IN_CONSULTATION:
            return await self._handle_in_consultation(input_data)

        if step == DoctorAssistanceStep.COMPLETED:
            return await self._handle_completed(input_data)

        raise ValueError(f"Unhandled doctor assistance step: {step}")

    async def _handle_idle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(
            "[DoctorAssistance] Received visit | "
            f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id} step={self.state.step}"
        )
        self.transition_to(DoctorAssistanceStep.READY)
        print(
            "[DoctorAssistance] Transitioned to READY | "
            f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id}"
        )
        return {
            "message": "Visit received. Ready to start consultation.",
            "visit_id": str(self.state.visit_id),
        }

    async def _handle_ready(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action")

        if action != "start_consultation":
            print(
                "[DoctorAssistance] Waiting for start_consultation | "
                f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id}"
            )
            return {
                "message": "Waiting for doctor to start consultation.",
                "expected_action": "start_consultation",
            }

        queue_date_raw = input_data.get("queue_date")
        if not queue_date_raw:
            print(
                "[DoctorAssistance] Missing queue_date | "
                f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id}"
            )
            return {"message": "queue_date is required to start consultation."}

        queue_date = date.fromisoformat(queue_date_raw)


        # 1️⃣ Logic delegates to QueueService (managed externally)
        # No HTTP call needed here as this is now a helper


        # 2️⃣ Update local state ONLY after success
        self.state.consultation_started_at = datetime.utcnow()
        self.transition_to(DoctorAssistanceStep.IN_CONSULTATION)
        print(
            "[DoctorAssistance] Consultation started | "
            f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id} "
            f"started_at={self.state.consultation_started_at.isoformat()}"
        )

        return {
            "message": "Consultation started successfully.",
            "visit_id": str(self.state.visit_id),
            "started_at": self.state.consultation_started_at.isoformat(),
        }

    async def _handle_in_consultation(
        self, input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        print(
            "[DoctorAssistance] In consultation | "
            f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id}"
        )
        action = input_data.get("action")

        if action == "save_notes":
            notes = input_data.get("notes")

            if not notes or len(notes.strip()) < 5:
                return {"message": "Consultation notes must be at least 5 characters."}

            consultation = await ConsultationService.upsert_notes(
                self.db,
                visit_id=self.state.visit_id,
                doctor_id=self.state.doctor_id,
                patient_id=self.state.patient_id,
                notes=notes,
                started_at=self.state.consultation_started_at,
            )

            self.state.consultation_notes = notes

            return {
                "message": "Consultation notes saved successfully.",
                "consultation_id": str(consultation.id),
            }
        
        if action == "add_prescription":
            medicine_name = input_data.get("medicine_name")

            if not medicine_name:
                return {
                    "message": "medicine_name is required."
                }

            item = await PrescriptionService.add_item(
                self.db,
                visit_id=self.state.visit_id,
                medicine_name=medicine_name,
                dosage=input_data.get("dosage"),
                frequency=input_data.get("frequency"),
                duration_days=input_data.get("duration_days"),
                instructions=input_data.get("instructions"),
            )

            self.state.prescriptions.append({
                "medicine_name": item.medicine_name,
                "dosage": item.dosage,
                "frequency": item.frequency,
                "duration_days": item.duration_days,
                "instructions": item.instructions,
            })

            return {
                "message": "Prescription item added.",
                "medicine_name": item.medicine_name,
            }

        if action == "end_consultation":
            # Check recursively called from QueueService
            skip_queue_call = input_data.get("skip_queue_call", False)
            
            if not skip_queue_call:
                # Delegate to Queue Service to handle full closure (queue + visit)
                # This avoids split-brain where agent is closed but queue entry is stuck
                await self.queue_client.end_consultation(
                    doctor_id=self.state.doctor_id,
                    visit_id=self.state.visit_id,
                    queue_date=datetime.utcnow().date(),
                )
            
            # The QueueService will call back (or we update local state)
            self.state.consultation_ended_at = datetime.utcnow()
            self.transition_to(DoctorAssistanceStep.COMPLETED)
            
            print(
                "[DoctorAssistance] Consultation ended via QueueService | "
                f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id} "
                f"ended_at={self.state.consultation_ended_at.isoformat()}"
            )
            return {
                "message": "Consultation completed.",
                "visit_id": str(self.state.visit_id),
            }
        return {
            "message": "Invalid action during consultation.",
            "allowed_actions": [
                "save_notes",
                "add_prescription",
                "end_consultation"
            ],
        }

    async def _handle_completed(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(
            "[DoctorAssistance] Consultation already completed | "
            f"visit_id={self.state.visit_id} doctor_id={self.state.doctor_id}"
        )
        return {
            "message": "Consultation already completed.",
            "visit_id": str(self.state.visit_id),
        }

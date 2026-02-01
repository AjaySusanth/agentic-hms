from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class DoctorAssistanceStep(str, Enum):
    IDLE = "idle"
    READY = "ready"
    IN_CONSULTATION = "in_consultation"
    COMPLETED = "completed"


class PrescriptionItem(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    instructions: Optional[str] = None


class LabOrderItem(BaseModel):
    test_name: str
    priority: Optional[str] = "routine"


class DoctorAssistanceState(BaseModel):
    # -------- Agent identity --------
    agent_name: str = "doctor_assistance_agent"
    step: DoctorAssistanceStep = DoctorAssistanceStep.IDLE

    # -------- Visit context (read-only) --------
    visit_id: UUID
    patient_id: UUID
    doctor_id: UUID
    token_number: Optional[int] = None
    department: Optional[str] = None
    symptoms_summary: Optional[str] = None

    # -------- Consultation lifecycle --------
    consultation_started_at: Optional[datetime] = None
    consultation_ended_at: Optional[datetime] = None

    # -------- Clinical data (owned by this agent) --------
    consultation_notes: Optional[str] = None
    prescriptions: List[PrescriptionItem] = []
    lab_orders: List[LabOrderItem] = []

    # -------- Metadata --------
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

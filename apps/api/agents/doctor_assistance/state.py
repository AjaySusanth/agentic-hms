from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class DoctorAssistanceState(BaseModel):
    visit_id: UUID
    patient_id: UUID
    doctor_id: str
    department: str
    symptoms_summary: str
    token_number: Optional[int] = None

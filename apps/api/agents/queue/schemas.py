from pydantic import BaseModel
from uuid import UUID
from datetime import date


class QueueIntakeRequest(BaseModel):
    visit_id: UUID
    patient_id: UUID
    doctor_id: UUID
    queue_date: date


class QueueIntakeResponse(BaseModel):
    accepted: bool
    token_number: int | None = None
    position: int | None = None
    estimated_wait_minutes: int | None = None
    reason: str | None = None


class CallNextRequest(BaseModel):
    doctor_id: UUID
    queue_date: date


class CallNextResponse(BaseModel):
    visit_id: UUID
    patient_id: UUID
    doctor_id: UUID
    token_number: int
    status: str

class EndConsultationRequest(BaseModel):
    doctor_id: UUID
    visit_id: UUID
    queue_date: date


class EndConsultationResponse(BaseModel):
    success: bool
    visit_id: UUID
    message: str
from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional,List


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

class CheckInRequest(BaseModel):
    visit_id: UUID
    queue_date: date


class CheckInResponse(BaseModel):
    success: bool
    visit_id: UUID
    status: str

class SkipRequest(BaseModel):
    visit_id: UUID
    doctor_id: UUID
    queue_date: date
    reason: str


class SkipResponse(BaseModel):
    success: bool
    visit_id: UUID
    status: str

class StartConsultationRequest(BaseModel):
    doctor_id: UUID
    visit_id: UUID
    queue_date: date


class StartConsultationResponse(BaseModel):
    success: bool
    visit_id: UUID
    status: str



class QueueStatusRequest(BaseModel):
    queue_date: date
    doctor_id: UUID
    role: str  # doctor | patient | receptionist
    visit_id: Optional[UUID] = None


# ---------- Shared ----------
class TokenInfo(BaseModel):
    token_number: int
    status: str


# ---------- Doctor ----------
class DoctorQueueStatus(BaseModel):
    role: str
    queue_open: bool
    current_token: Optional[int]
    current_visit_id: Optional[UUID]
    called: Optional[TokenInfo]
    next_waiting: List[TokenInfo]
    counts: dict


# ---------- Patient ----------
class PatientQueueStatus(BaseModel):
    role: str
    visit_id: UUID
    token_number: int
    status: str
    current_token: Optional[int]
    patients_ahead: int
    estimated_wait_minutes: int
    message: Optional[str] = None


# ---------- Reception ----------
class ReceptionQueueStatus(BaseModel):
    role: str
    queue_date: date
    doctor_id: UUID
    total_visits: int
    completed: int
    in_progress: int
    waiting: int
    skipped: int
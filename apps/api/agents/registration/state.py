from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional,List
from uuid import UUID
from datetime import datetime



class RegistrationStep(str, Enum):
    COLLECT_PHONE = "collect_phone"
    PATIENT_LOOKUP = "patient_lookup"
    COLLECT_PATIENT_DETAILS = "collect_patient_details"
    COLLECT_SYMPTOMS = "collect_symptoms"
    RESOLVE_DEPARTMENT = "resolve_department"
    SELECT_DOCTOR = "select_doctor"
    CREATE_VISIT = "create_visit"
    HANDOFF_COMPLETE = "handoff_complete"


class RegistrationAgentState(BaseModel):
    # --- Meta ---
    agent_name: str = "registration_agent"
    step: RegistrationStep = RegistrationStep.COLLECT_PHONE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Patient Identification ---
    phone_number: Optional[str] = None
    patient_id: Optional[UUID] = None
    is_existing_patient: Optional[bool] = None

    # --- Patient Details (if new) ---
    full_name: Optional[str] = None
    age: Optional[int] = None
    abha_id: Optional[str] = None

    # --- Visit Intent ---
    symptoms_raw: Optional[str] = None
    symptoms_summary: Optional[str] = None

    # --- Resolution ---
    department_suggested: Optional[str] = None
    department_confidence: Optional[float] = None
    department_reasoning: Optional[List[str]] = None

    department_final: Optional[str] = None
    department_id: Optional[UUID] = None
    department_overridden: bool = False

    # --- Visit ---
    doctor_id: Optional[UUID] = None
    visit_id: Optional[UUID] = None
    
    # --- Handoff State ---
    handoff_processed: bool = False
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class ChatbotStep(str, Enum):
    GREETING = "greeting"
    COLLECT_SYMPTOMS = "collect_symptoms"
    DETECT_INTENT = "detect_intent"
    DISCOVER_HOSPITALS = "discover_hospitals"
    SELECT_HOSPITAL = "select_hospital"
    PROXY_REGISTRATION = "proxy_registration"      # Forwarding to Registration Agent
    EXTERNAL_HANDOFF = "external_handoff"           # For hotel booking, etc.
    COMPLETED = "completed"


class HospitalOption(BaseModel):
    hospital_id: UUID
    hospital_name: str
    location: str
    doctors: List[Dict[str, Any]] = []  # [{name, specialization, id}]


class ChatbotOrchestratorState(BaseModel):
    # --- Meta ---
    agent_name: str = "chatbot_orchestrator"
    step: ChatbotStep = ChatbotStep.GREETING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Intent Detection ---
    detected_intent: Optional[str] = None           # "medical", "hotel_booking", "general_query"
    department_hint: Optional[str] = None            # LLM-suggested department
    intent_confidence: Optional[float] = None

    # --- Symptoms ---
    symptoms_raw: Optional[str] = None

    # --- Hospital Discovery ---
    available_hospitals: List[HospitalOption] = []
    selected_hospital_id: Optional[UUID] = None
    selected_hospital_name: Optional[str] = None

    # --- Proxy Mode (Registration Agent) ---
    delegated_session_id: Optional[UUID] = None     # Registration agent session ID
    registration_step: Optional[str] = None          # Current step of the delegated Registration Agent
    proxy_phone_number: Optional[str] = None

    # --- External System ---
    external_system: Optional[str] = None           # "hotel_booking", etc.

    # --- Conversation History ---
    messages: List[Dict[str, str]] = []             # [{role: "user"/"bot", content: "..."}]

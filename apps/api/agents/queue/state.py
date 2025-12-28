from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, time, datetime


class QueueAgentState(BaseModel):
    agent_name: str = "queue_agent"

    # Scope
    doctor_id: UUID
    queue_date: date

    # Shift configuration (MVP: single shift per day)
    shift_start_time: time
    shift_end_time: time

    # Queue control
    queue_open: bool = True
    max_queue_size: Optional[int] = None
    avg_consult_time_minutes: int = 10

    # Progress tracking
    current_token: int = 0
    current_visit_id: Optional[UUID] = None

    # Explainability
    last_event_type: Optional[str] = None
    last_event_reason: Optional[str] = None
    last_updated_by: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

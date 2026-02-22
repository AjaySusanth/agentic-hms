from typing import Any, Dict, Optional
from pydantic import BaseModel

from agents.registration.state import RegistrationAgentState
from uuid import UUID

class AgentRequest(BaseModel):
    session_id: Optional[UUID] = None
    hospital_id: Optional[UUID] = None
    input: Dict[str, Any]
    


class AgentResponse(BaseModel):
    session_id: UUID
    response: Dict[str, Any]
    state: RegistrationAgentState

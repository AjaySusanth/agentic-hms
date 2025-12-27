from typing import Any, Dict, Optional
from pydantic import BaseModel

from agents.registration.state import RegistrationAgentState


class AgentRequest(BaseModel):
    state: Optional[RegistrationAgentState] = None
    input: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    response: Dict[str, Any]
    state: RegistrationAgentState

"""
State model for template-driven workflow sessions.
Analogous to ChatbotOrchestratorState but generic.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class TemplateWorkflowState(BaseModel):
    """
    Tracks the state of a template-driven workflow session.
    Stored via AgentSessionService, just like chatbot sessions.
    """
    agent_name: str = "template_engine"
    service_type: str                      # e.g. "restaurant_reservation"
    service_name: str                      # e.g. "Tasty Bites Restaurant"
    current_step_id: str                   # Which step we're on
    collected_data: Dict[str, Any] = {}    # All user inputs collected so far
    api_results: Dict[str, Any] = {}       # Cached API responses (keyed by action name)
    step: str = "running"                  # "running" | "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Conversation history
    messages: List[Dict[str, str]] = []
    last_bot_message: Optional[str] = None

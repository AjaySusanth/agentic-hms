from typing import Dict, Any
from agents.doctor_assistance.state import DoctorAssistanceState


class DoctorAssistanceAgent:
    """
    Triggered ONLY by Queue Agent when consultation starts.
    """

    def __init__(self, state: DoctorAssistanceState):
        self.state = state

    def handle(self) -> Dict[str, Any]:
        return {
            "status": "ready_for_consultation",
            "visit_id": str(self.state.visit_id),
            "doctor_id": str(self.state.doctor_id),
            "token_number": self.state.token_number,
        }

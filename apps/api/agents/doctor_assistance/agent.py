from typing import Dict, Any

from agents.doctor_assistance.state import DoctorAssistanceState


class DoctorAssistanceAgent:
    """
    Stub for Doctor Assistance Agent.
    Will be expanded later.
    """

    def __init__(self, state: DoctorAssistanceState):
        self.state = state

    def handle(self) -> Dict[str, Any]:
        """
        Entry point for doctor-side workflow.
        """
        # For now, just acknowledge receipt
        return {
            "status": "received",
            "visit_id": str(self.state.visit_id),
            "doctor_id": self.state.doctor_id,
            "token_number": self.state.token_number,
        }

from typing import Dict, Any
import httpx
from datetime import date

QUEUE_AGENT_URL = "http://localhost:8000/agents/queue/intake"


async def handoff_to_queue_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends visit to Queue Agent for intake.
    No business logic here.
    """

    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            QUEUE_AGENT_URL,
            json={
                "visit_id": str(payload["visit_id"]),
                "patient_id": str(payload["patient_id"]),
                "doctor_id": str(payload["doctor_id"]),
                "queue_date": payload["queue_date"].isoformat()
                if isinstance(payload["queue_date"], date)
                else payload["queue_date"],
            },
        )

    response.raise_for_status()
    return response.json()

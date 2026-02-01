import httpx
from uuid import UUID
from datetime import date
from typing import Dict


class QueueAgentClient:
    """
    Thin HTTP client for Queue Agent delegation.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def start_consultation(
        self,
        *,
        doctor_id: UUID,
        visit_id: UUID,
        queue_date: date,
    ) -> Dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/agents/queue/start-consultation",
                json={
                    "doctor_id": str(doctor_id),
                    "visit_id": str(visit_id),
                    "queue_date": queue_date.isoformat(),
                },
                timeout=5.0,
            )

        if resp.status_code != 200:
            raise ValueError(
                f"Queue Agent rejected start-consultation: {resp.text}"
            )

        return resp.json()

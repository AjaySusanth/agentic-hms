import httpx
from uuid import UUID
from typing import Dict, Any, Optional


BASE_URL = "http://localhost:8000/api"


class HospitalClient:
    """
    HTTP client for the Chatbot Orchestrator to interact with
    hospital-specific agents (Registration, Queue, etc.)
    """

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def start_registration(
        self,
        hospital_id: UUID,
        phone_number: str,
    ) -> Dict[str, Any]:
        """Start a new registration session at a specific hospital."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/agents/registration/message",
                json={
                    "hospital_id": str(hospital_id),
                    "input": {"phone_number": phone_number},
                },
            )
        resp.raise_for_status()
        return resp.json()

    async def continue_registration(
        self,
        session_id: UUID,
        hospital_id: UUID,
        input_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Continue an existing registration session with user input."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.base_url}/agents/registration/message",
                json={
                    "session_id": str(session_id),
                    "hospital_id": str(hospital_id),
                    "input": input_data,
                },
            )
        resp.raise_for_status()
        return resp.json()

    async def get_departments(
        self, hospital_id: UUID
    ) -> list:
        """Get all departments for a specific hospital."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{self.base_url}/doctors/departments",
                params={"hospital_id": str(hospital_id)},
            )
        resp.raise_for_status()
        return resp.json()

    async def get_doctors_by_department(
        self, hospital_id: UUID, department_name: str
    ) -> list:
        """Get available doctors for a department at a specific hospital."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{self.base_url}/doctors/available",
                params={
                    "hospital_id": str(hospital_id),
                    "department": department_name,
                },
            )
        resp.raise_for_status()
        return resp.json()

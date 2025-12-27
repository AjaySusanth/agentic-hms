import asyncio
import sys
from pathlib import Path

# Add apps/api to Python path so we can import db module
repo_root = Path(__file__).resolve().parents[1]
api_path = repo_root / "apps" / "api"
sys.path.insert(0, str(api_path))

from db.session import AsyncSessionLocal
from services.patient_service import PatientService


async def test():
    async with AsyncSessionLocal() as db:
        patient = await PatientService.create(
            db,
            full_name="Test User1",
            age=28,
            contact_number="8888888889",
        )
        print(patient)

        found = await PatientService.get_by_phone(db, "8888888889")
        print(found)

asyncio.run(test())

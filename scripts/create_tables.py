import asyncio
import sys
from pathlib import Path

# Add apps/api to Python path so we can import db module
repo_root = Path(__file__).resolve().parents[1]
api_path = repo_root / "apps" / "api"
sys.path.insert(0, str(api_path))

from db.session import engine
from db.base import Base

# Import models so metadata is registered
from models import patient, department, doctor, visit # noqa


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")


asyncio.run(create_tables())

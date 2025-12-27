import asyncio
import sys
from pathlib import Path

# Add apps/api to Python path so we can import db module
repo_root = Path(__file__).resolve().parents[1]
api_path = repo_root / "apps" / "api"
sys.path.insert(0, str(api_path))

from db.session import engine

async def test_connection():
    async with engine.begin() as conn:
        await conn.run_sync(lambda _: None)
    print("✅ Database connection successful")

asyncio.run(test_connection())

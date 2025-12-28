from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from uuid import UUID

from db.session import get_db_session
from services.queue_service import QueueIntakeService
from agents.queue.schemas import QueueIntakeRequest, QueueIntakeResponse

router = APIRouter(prefix="/agents/queue", tags=["Queue Agent"])


@router.post("/intake", response_model=QueueIntakeResponse)
async def queue_intake(
    request: QueueIntakeRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        result = await QueueIntakeService.intake(db, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

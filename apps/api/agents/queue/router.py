from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from uuid import UUID

from db.session import get_db_session
from services.queue_service import QueueService
from agents.queue.schemas import QueueIntakeRequest, QueueIntakeResponse,CallNextRequest,CallNextResponse,EndConsultationRequest,EndConsultationResponse

router = APIRouter(prefix="/agents/queue", tags=["Queue Agent"])


@router.post("/intake", response_model=QueueIntakeResponse)
async def queue_intake(
    request: QueueIntakeRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        result = await QueueService.intake(db, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/call-next", response_model=CallNextResponse)
async def call_next_patient(
    request: CallNextRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.call_next(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/end-consultation", response_model=EndConsultationResponse)
async def end_consultation(
    request: EndConsultationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.end_consultation(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

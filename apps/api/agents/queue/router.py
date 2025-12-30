from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from uuid import UUID

from db.session import get_db_session
from services.queue_service import QueueService
from agents.queue.schemas import QueueIntakeRequest, QueueIntakeResponse,CallNextRequest,CallNextResponse,EndConsultationRequest,EndConsultationResponse, CheckInRequest,CheckInResponse,SkipRequest,SkipResponse,StartConsultationRequest,StartConsultationResponse,QueueStatusRequest

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

@router.post("/check-in", response_model=CheckInResponse)
async def check_in_patient(
    request: CheckInRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.check_in(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/skip", response_model=SkipResponse)
async def skip_patient(
    request: SkipRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.skip_patient(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/start-consultation", response_model=StartConsultationResponse)
async def start_consultation(
    request: StartConsultationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.start_consultation(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
async def queue_status(
    request: QueueStatusRequest = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        return await QueueService.get_status(db, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
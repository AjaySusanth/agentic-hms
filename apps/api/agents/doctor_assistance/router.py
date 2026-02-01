from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID

from db.session import get_db_session
from agents.doctor_assistance.agent import DoctorAssistanceAgent
from agents.doctor_assistance.state import DoctorAssistanceState
from services.agent_session_service import AgentSessionService, agent_sessions

router = APIRouter(
    prefix="/agents/doctor-assistance",
    tags=["Doctor Assistance Agent"],
)


class DoctorActionByVisitRequest(BaseModel):
    visit_id: UUID
    input: dict


@router.post("/handle")
async def handle_doctor_action(
    state: DoctorAssistanceState,
    input: dict,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        agent = DoctorAssistanceAgent(state)
        agent.db = db
        response = await agent.handle(input)
        return {
            "response": response,
            "state": agent.state,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/handle-by-visit")
async def handle_doctor_action_by_visit(
    request: DoctorActionByVisitRequest,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        print(
            f"[DoctorAssistance Router] Looking for session with visit_id={request.visit_id}"
        )
        
        result = await db.execute(
            select(agent_sessions)
            .where(agent_sessions.c.state["visit_id"].astext == str(request.visit_id))
            .order_by(agent_sessions.c.created_at.desc())
            .limit(1)
        )
        row = result.first()
        
        print(f"[DoctorAssistance Router] Query result: {row}")

        if not row:
            # Debug: fetch all sessions to see what's there
            all_result = await db.execute(
                select(agent_sessions).order_by(agent_sessions.c.created_at.desc()).limit(5)
            )
            all_rows = all_result.fetchall()
            print(f"[DoctorAssistance Router] Available sessions (last 5):")
            for r in all_rows:
                print(f"  - session_id={r[0]}, agent_name={r[1]}, state={r[2]}")
            
            raise HTTPException(
                status_code=404,
                detail=f"No doctor assistance session found for visit_id: {request.visit_id}. The doctor must call next patient first to initialize the consultation session.",
            )

        session_id = row[0]
        state_dict = row[2]
        print(f"[DoctorAssistance Router] Found session {session_id}, state={state_dict}")
        
        state = DoctorAssistanceState(**state_dict)

        agent = DoctorAssistanceAgent(state, db=db)
        response = await agent.handle(request.input)
        
        print(
            f"[DoctorAssistance Router] Action completed: {request.input.get('action')}, "
            f"new_step={agent.state.step}"
        )

        await AgentSessionService.update(
            db,
            session_id,
            agent.state.dict(),
        )

        return {
            "response": response,
            "state": agent.state,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

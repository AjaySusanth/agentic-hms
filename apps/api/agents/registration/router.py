from fastapi import APIRouter,Depends

from sqlalchemy.ext.asyncio import AsyncSession

from agents.registration.agent import RegistrationAgent
from agents.registration.state import RegistrationAgentState, RegistrationStep
from schemas.agent import AgentRequest, AgentResponse
from db.session import get_db_session
from services.agent_session_service import AgentSessionService

router = APIRouter(prefix="/agents/registration", tags=["Registration Agent"])


@router.post("/message", response_model=AgentResponse)
async def handle_registration_message(payload: AgentRequest, db: AsyncSession = Depends(get_db_session),):

    # -------------------------------------------------
    # 1️⃣ Load or create session
    # -------------------------------------------------

    if payload.session_id:
        state_data = await AgentSessionService.get(
            db,
            payload.session_id,
        )
        if not state_data:
            raise ValueError("Invalid session_id")

        state = RegistrationAgentState(**state_data)
        session_id = payload.session_id
    else:
        state = RegistrationAgentState(
            step=RegistrationStep.COLLECT_PHONE,
            hospital_id=payload.hospital_id
        )
        session_id = await AgentSessionService.create(
            db,
            agent_name=state.agent_name,
            state=state.model_dump(),
        )
    
    # -------------------------------------------------
    # 2️⃣ Run agent
    # -------------------------------------------------
    agent = RegistrationAgent(state=state, db=db)
    response = await agent.handle(payload.input)

    # -------------------------------------------------
    # 3️⃣ Persist updated state
    # -------------------------------------------------
    await AgentSessionService.update(
        db,
        session_id=session_id,
        state=agent.state.model_dump(),
    )

    return AgentResponse(
        session_id=session_id,
        response=response,
        state=agent.state.model_dump(),
    )


'''
model_dump() is a method from Pydantic V2 (the library powering data validation in FastAPI).
It converts your fancy Pydantic object into a plain Python dictionary.


Example:
state.model_dump():
Input: A RegistrationAgentState object (e.g., step=COLLECT_PHONE, phone="123").
Output: A standard Python dict: {'step': 'COLLECT_PHONE', 'phone': '123'}.
'''
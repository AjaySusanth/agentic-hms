from fastapi import APIRouter,Depends

from sqlalchemy.ext.asyncio import AsyncSession

from agents.registration.agent import RegistrationAgent
from agents.registration.state import RegistrationAgentState, RegistrationStep
from schemas.agent import AgentRequest, AgentResponse
from db.session import get_db_session
router = APIRouter(prefix="/agents/registration", tags=["Registration Agent"])


@router.post("/message", response_model=AgentResponse)
async def handle_registration_message(payload: AgentRequest, db: AsyncSession = Depends(get_db_session),):
    # 1️⃣ Initialize or restore state
    state = payload.state or RegistrationAgentState(
        step=RegistrationStep.COLLECT_PHONE
    )

    # 2️⃣ Create agent
    agent = RegistrationAgent(state,db=db)

    # 3️⃣ Handle input
    response = await agent.handle(payload.input or {})

    # 4️⃣ Return response + updated state
    return AgentResponse(
        response=response,
        state=agent.state
    )

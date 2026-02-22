from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import UUID

from db.session import get_db_session
from services.agent_session_service import AgentSessionService
from agents.chatbot.agent import ChatbotOrchestratorAgent
from agents.chatbot.state import ChatbotOrchestratorState, ChatbotStep


router = APIRouter(prefix="/chatbot", tags=["Chatbot"])


# ──────────────────────────────────────────────
# Request / Response Schemas
# ──────────────────────────────────────────────
class ChatMessageRequest(BaseModel):
    message: str = ""
    # Optional structured input (from frontend buttons)
    doctor_id: Optional[str] = None
    department: Optional[str] = None
    confirm: Optional[str] = None


class ChatSessionResponse(BaseModel):
    session_id: UUID
    message: str
    step: str
    session_data: Optional[Dict[str, Any]] = None


# ──────────────────────────────────────────────
# POST /api/chatbot/session — Start new chat
# ──────────────────────────────────────────────
@router.post("/session", response_model=ChatSessionResponse)
async def start_chat_session(
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new chatbot session and return the greeting."""
    state = ChatbotOrchestratorState(step=ChatbotStep.GREETING)

    agent = ChatbotOrchestratorAgent(state, db=db)
    result = await agent.handle({})

    # Save session
    session_id = await AgentSessionService.create(
        db,
        agent_name="chatbot_orchestrator",
        state=agent.state.model_dump(),
    )

    return ChatSessionResponse(
        session_id=session_id,
        message=result["message"],
        step=result["step"],
        session_data=result.get("session_data"),
    )


# ──────────────────────────────────────────────
# POST /api/chatbot/session/{id}/message — Send message
# ──────────────────────────────────────────────
@router.post("/session/{session_id}/message", response_model=ChatSessionResponse)
async def send_chat_message(
    session_id: UUID,
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Send a message to an existing chatbot session."""

    # Load session
    session = await AgentSessionService.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    state = ChatbotOrchestratorState(**session)

    # Track user message
    state.messages.append({"role": "user", "content": request.message})

    # Build input dict
    user_input = {"message": request.message}
    if request.doctor_id:
        user_input["doctor_id"] = request.doctor_id
    if request.department:
        user_input["department"] = request.department
    if request.confirm:
        user_input["confirm"] = request.confirm

    # Run agent
    agent = ChatbotOrchestratorAgent(state, db=db)
    result = await agent.handle(user_input)

    # Save updated state
    await AgentSessionService.update(
        db,
        session_id,
        agent.state.model_dump(),
    )

    return ChatSessionResponse(
        session_id=session_id,
        message=result["message"],
        step=result["step"],
        session_data=result.get("session_data"),
    )


# ──────────────────────────────────────────────
# GET /api/chatbot/session/{id} — Get session state
# ──────────────────────────────────────────────
@router.get("/session/{session_id}")
async def get_chat_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """Retrieve the current state of a chatbot session."""
    session = await AgentSessionService.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    state = ChatbotOrchestratorState(**session)

    return {
        "session_id": session_id,
        "step": state.step.value,
        "messages": state.messages,
        "detected_intent": state.detected_intent,
        "selected_hospital": state.selected_hospital_name,
    }

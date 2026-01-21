from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.langgraph.session_store import get_session, save_session
from app.langgraph.state import InterviewState
from app.agents.chat_assessment_agent import ChatAssessmentAgent
from app.api.candidate import candidate_cache
import json

router = APIRouter()
agent = ChatAssessmentAgent()

@router.websocket("/ws/chat/{candidate_id}")
async def chat_ws(websocket: WebSocket, candidate_id: str):
    await websocket.accept()

    profile_json = candidate_cache.get(candidate_id)
    if not profile_json:
        await websocket.send_text("Invalid candidate_id")
        await websocket.close()
        return

    profile = json.loads(profile_json)

    state: InterviewState = {
        "candidate_id": candidate_id,
        "candidate_profile": profile,
        "chat_history": [],
        "technical_score": 0.0,
        "behavioral_score": 0.0,
        "final_report": {},
        "requires_hr": False,
        "chat_complete": False
    }

    save_session(candidate_id, state)

    await websocket.send_text("Chat-based assessment started. Tell me about yourself.")

    try:
        while True:
            user_message = await websocket.receive_text()

            state = get_session(candidate_id)

            if state.get("chat_complete"):
                await websocket.send_text("Chat assessment already completed. Thank you!")
                break

            state = agent.run(state, user_message)
            save_session(candidate_id, state)

            await websocket.send_text(state["chat_history"][-1]["message"])

            if state.get("chat_complete"):
                await websocket.send_text("Closing chat. You can proceed to technical & behavioral interviews.")
                await websocket.close()

    except WebSocketDisconnect:
        print(f"Chat ended for {candidate_id}")

from app.langgraph.state import InterviewState

SESSION_STORE: dict[str, InterviewState] = {}

def get_session(candidate_id: str) -> InterviewState | None:
    return SESSION_STORE.get(candidate_id)

def save_session(candidate_id: str, state: InterviewState):
    SESSION_STORE[candidate_id] = state

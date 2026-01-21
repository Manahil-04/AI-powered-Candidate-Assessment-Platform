from app.langgraph.state import InterviewState

class HRHandoffAgent:
    def run(self, state: InterviewState) -> InterviewState:
        if state["requires_hr"]:
            state["chat_history"].append({
                "role": "system",
                "message": "Escalated to HR for manual review."
            })
        return state

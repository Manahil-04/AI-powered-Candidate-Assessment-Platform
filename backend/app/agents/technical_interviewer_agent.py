from app.langgraph.state import InterviewState

class TechnicalInterviewerAgent:
    def run(self, state: InterviewState) -> InterviewState:
        state["technical_score"] += 10

        state["chat_history"].append({
            "role": "system",
            "message": "Technical interview completed."
        })

        return state

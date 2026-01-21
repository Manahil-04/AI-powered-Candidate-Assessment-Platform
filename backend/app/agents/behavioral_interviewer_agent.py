from app.langgraph.state import InterviewState

class BehavioralInterviewerAgent:
    def run(self, state: InterviewState) -> InterviewState:
        state["behavioral_score"] += 10

        state["chat_history"].append({
            "role": "system",
            "message": "Behavioral interview completed."
        })

        return state

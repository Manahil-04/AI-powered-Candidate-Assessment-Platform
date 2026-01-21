from app.langgraph.state import InterviewState

class EvaluationAgent:
    def run(self, state: InterviewState) -> InterviewState:
        overall = (state["technical_score"] + state["behavioral_score"]) / 2

        state["final_report"] = {
            "technical_score": state["technical_score"],
            "behavioral_score": state["behavioral_score"],
            "overall_score": overall,
            "recommendation": "Strong Hire" if overall >= 15 else "Needs Review"
        }

        state["requires_hr"] = overall < 15

        state["chat_history"].append({
            "role": "system",
            "message": "Evaluation completed."
        })

        return state

from app.langgraph.state import InterviewState

class ProfileAnalyzerAgent:
    def run(self, state: InterviewState) -> InterviewState:
        profile = state["candidate_profile"]

        state["technical_score"] = len(profile.get("skills", [])) * 1.5
        state["behavioral_score"] = 5.0

        state["chat_history"].append({
            "role": "system",
            "message": "Profile analyzed."
        })

        return state

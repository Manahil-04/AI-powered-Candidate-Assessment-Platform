from app.core.config import settings
import google.generativeai as genai
from app.langgraph.state import InterviewState

genai.configure(api_key=settings.GOOGLE_API_KEY)

class ChatAssessmentAgent:
    """
    Chat-based AI interviewer that asks exactly 2 questions.
    """

    MAX_QUESTIONS = 2

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")

    def run(self, state: InterviewState, user_message: str) -> InterviewState:
        """
        Process candidate's message and generate next AI question.
        Stops after MAX_QUESTIONS.
        """
        state["chat_history"].append({
            "role": "candidate",
            "message": user_message
        })

        questions_asked = sum(1 for msg in state["chat_history"] if msg["role"] == "assistant")

        if questions_asked >= self.MAX_QUESTIONS:
            state["chat_history"].append({
                "role": "assistant",
                "message": "Thank you! The chat assessment is now complete."
            })
            state["chat_complete"] = True
            return state

        context = self._build_context(state)

        response = self.model.generate_content(
            f"""
You are a professional AI interviewer.

Candidate profile:
{context}

Conversation so far:
{state['chat_history']}

Candidate says:
{user_message}

Respond with exactly ONE interview question. Do not include explanations.
"""
        )

        ai_reply = response.text.strip()

        state["chat_history"].append({
            "role": "assistant",
            "message": ai_reply
        })

        return state

    def _build_context(self, state: InterviewState) -> str:
        profile = state["candidate_profile"]
        return f"""
Name: {profile.get('name')}
Skills: {profile.get('skills')}
Experience: {profile.get('experience')}
Projects: {profile.get('projects')}
"""

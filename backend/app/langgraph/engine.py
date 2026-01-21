from langgraph.graph import StateGraph, END

from app.langgraph.state import InterviewState
from app.agents.profile_analyzer_agent import ProfileAnalyzerAgent
from app.agents.technical_interviewer_agent import TechnicalInterviewerAgent
from app.agents.behavioral_interviewer_agent import BehavioralInterviewerAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.hr_handoff_agent import HRHandoffAgent

class LangGraphEngine:
    def __init__(self):
        self.graph = StateGraph(InterviewState)

        self.graph.add_node("profile_analyzer", ProfileAnalyzerAgent().run)
        self.graph.add_node("technical_interviewer", TechnicalInterviewerAgent().run)
        self.graph.add_node("behavioral_interviewer", BehavioralInterviewerAgent().run)
        self.graph.add_node("evaluation", EvaluationAgent().run)
        self.graph.add_node("hr_handoff", HRHandoffAgent().run)

        self.graph.set_entry_point("profile_analyzer")

        self.graph.add_edge("profile_analyzer", "technical_interviewer")
        self.graph.add_edge("technical_interviewer", "behavioral_interviewer")
        self.graph.add_edge("behavioral_interviewer", "evaluation")

        self.graph.add_conditional_edges(
            "evaluation",
            lambda state: "hr" if state["requires_hr"] else "end",
            {
                "hr": "hr_handoff",
                "end": END
            }
        )

        self.graph.add_edge("hr_handoff", END)

        self.app = self.graph.compile()

    def run(self, state: InterviewState) -> InterviewState:
        return self.app.invoke(state)

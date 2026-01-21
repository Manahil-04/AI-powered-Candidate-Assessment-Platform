from typing import TypedDict, List, Dict, Any

class InterviewState(TypedDict):
    candidate_id: str
    candidate_profile: Dict[str, Any]
    chat_history: List[Dict[str, str]]
    technical_score: float
    behavioral_score: float
    final_report: Dict[str, Any]
    requires_hr: bool

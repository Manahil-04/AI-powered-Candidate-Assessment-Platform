from typing import Dict, List
from app.models.schemas import CandidateProfile

candidate_kb: Dict[str, Dict] = {}

def add_candidate_to_kb(candidate_profile: CandidateProfile) -> str:
    candidate_id = candidate_profile.name.replace(" ", "_").lower()  
    candidate_kb[candidate_id] = {
        "profile": candidate_profile.dict(),
        "chat_history": [],
        "technical_score": None,
        "behavioral_score": None,
        "final_report": {},
        "requires_hr": False
    }
    return candidate_id

def get_candidate_from_kb(candidate_id: str) -> Dict:
    return candidate_kb.get(candidate_id)

def update_candidate_chat(candidate_id: str, agent_msg: Dict):
    if candidate_id in candidate_kb:
        candidate_kb[candidate_id]["chat_history"].append(agent_msg)

def update_candidate_scores(candidate_id: str, technical_score: float, behavioral_score: float):
    if candidate_id in candidate_kb:
        candidate_kb[candidate_id]["technical_score"] = technical_score
        candidate_kb[candidate_id]["behavioral_score"] = behavioral_score

def update_final_report(candidate_id: str, report: Dict, requires_hr: bool = False):
    if candidate_id in candidate_kb:
        candidate_kb[candidate_id]["final_report"] = report
        candidate_kb[candidate_id]["requires_hr"] = requires_hr

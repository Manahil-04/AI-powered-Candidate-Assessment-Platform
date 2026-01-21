from fastapi import APIRouter, File, UploadFile
from app.models.schemas import CandidateProfile
from app.ingestion.github import fetch_github_profile
from app.ingestion.resume_parser import parse_resume
from app.langgraph.engine import LangGraphEngine
from app.langgraph.state import InterviewState
import os, uuid, json

router = APIRouter(prefix="/candidate", tags=["candidate"])

candidate_cache = {} 

@router.post("/ingest")
def ingest_candidate(
    github_url: str = None,
    resume_file: UploadFile = File(...)
):
    # Save PDF temporarily
    pdf_path = f"temp_{resume_file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(resume_file.file.read())

    profile: CandidateProfile = parse_resume(pdf_path)
    os.remove(pdf_path)

    if github_url:
        username = github_url.rstrip("/").split("/")[-1]
        github_data = fetch_github_profile(username)
        profile.skills = list(set(profile.skills + github_data.get("top_languages", [])))

    candidate_id = str(uuid.uuid4())
    candidate_cache[candidate_id] = profile.json()

    return {
        "candidate_id": candidate_id,
        "profile": profile.dict()
    }


@router.post("/assess")
def assess_candidate(candidate_id: str):
    profile_json = candidate_cache.get(candidate_id)
    if not profile_json:
        return {"error": "Invalid candidate_id"}

    profile = CandidateProfile.parse_raw(profile_json)

    state: InterviewState = {
        "candidate_id": candidate_id,
        "candidate_profile": profile.dict(),
        "chat_history": [],   
        "technical_score": 0.0,
        "behavioral_score": 0.0,
        "final_report": {},
        "requires_hr": False,
        "last_user_message": ""
    }

    engine = LangGraphEngine()
    final_state = engine.run(state)

    return {
        "candidate_name": profile.name,
        "technical_score": final_state["technical_score"],
        "behavioral_score": final_state["behavioral_score"],
        "final_report": final_state["final_report"],
        "requires_hr": final_state["requires_hr"],
        "projects_reviewed": profile.projects
    }

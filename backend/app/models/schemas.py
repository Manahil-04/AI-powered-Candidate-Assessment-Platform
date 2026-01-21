from pydantic import BaseModel
from typing import List, Optional

class CandidateInput(BaseModel):
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_text: Optional[str] = None

class Experience(BaseModel):
    company: str
    role: str
    years: float

class CandidateProfile(BaseModel):
    name: str
    experience: List[Experience]
    skills: List[str]
    education: str
    projects: List[str] = []

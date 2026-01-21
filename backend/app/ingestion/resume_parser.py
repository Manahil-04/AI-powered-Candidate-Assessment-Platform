import pdfplumber
import re
from typing import List
from app.models.schemas import CandidateProfile, Experience

def parse_resume(pdf_path: str) -> CandidateProfile:
    """
    Parse a PDF resume into a structured CandidateProfile.
    Extracts:
    - name
    - experience
    - skills
    - education
    - projects (only project names)
    """

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    name = lines[0] if lines else "Unknown"

    experience: List[Experience] = []
    exp_lines = [l for l in lines if re.search(r"\b(?:Engineer|Developer|Manager|Intern|AI|Software)\b", l)]
    for line in exp_lines:
        parts = re.split(r"-|,", line)
        if len(parts) >= 2:
            role = parts[0].strip()
            company = parts[1].strip()
            experience.append(Experience(company=company, role=role, years=1))

    skills = []
    skills_keywords = ["Python", "Java", "C++", "FastAPI", "GitHub", "SQL", "JavaScript", "TypeScript", "HTML", "CSS"]
    for kw in skills_keywords:
        if kw.lower() in text.lower():
            skills.append(kw)
    skills = list(set(skills)) 

    education_match = re.search(r"(BSc|MSc|PhD|Bachelor|Master|University.*)", text, re.IGNORECASE)
    education = education_match.group(0) if education_match else "Unknown"

    projects: List[str] = []
    project_section = False

    for line in lines:
        if re.search(r"\b(Project|Projects)\b", line, re.IGNORECASE):
            project_section = True
            continue

        if project_section:
            if line:
                name_only = line.split("|")[0].strip()
                name_only = re.sub(r"^[•\-\*]\s*", "", name_only)
                if name_only:
                    projects.append(name_only)
            if re.match(r"^[A-Z][A-Za-z\s]+$", line.strip()):
                break

    projects = projects[:5]

    profile = CandidateProfile(
        name=name,
        experience=experience,
        skills=skills,
        education=education,
        projects=projects
    )

    return profile

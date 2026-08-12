# AI-Powered Candidate Assessment Platform

An AI-powered candidate assessment backend that combines resume analysis, GitHub profile enrichment, automated technical and behavioral assessment, and conversational AI interviewing into a single assessment workflow.

The platform is designed to give recruiters a structured view of a candidate's profile and assessment results while allowing candidates to interact with an AI interviewer through a real-time WebSocket connection.

## Overview

The platform takes a candidate's resume as the primary input and can optionally enrich the candidate profile using their public GitHub account.

The assessment workflow is orchestrated with **LangGraph** and follows a defined sequence:

```text
Candidate Resume
      │
      ▼
Resume Parser
      │
      ├──────────────► GitHub Profile Enrichment
      │
      ▼
Candidate Profile
      │
      ▼
Profile Analysis
      │
      ▼
Technical Assessment
      │
      ▼
Behavioral Assessment
      │
      ▼
Evaluation
      │
      ├── Strong Hire ──────► Final Report
      │
      └── Needs Review ─────► HR Handoff
```

In parallel, candidates can participate in a conversational assessment through a WebSocket endpoint. The chat interviewer uses **Gemini 2.5 Flash-Lite** to generate interview questions based on the candidate's parsed profile and previous responses.

## Key Features

### Resume Ingestion

Candidates can upload a PDF resume through the candidate ingestion endpoint.

The resume parser extracts:

* Candidate name
* Work experience
* Skills
* Education
* Project names

PDF text extraction is handled with `pdfplumber`, while regular expressions are used to identify experience, education, skills, and project sections.

### GitHub Profile Enrichment

Candidates can optionally provide a GitHub profile URL during ingestion.

The backend uses GitHub's public API to retrieve information including:

* GitHub username
* Number of public repositories
* Followers
* Repository languages
* Total repository stars

The detected programming languages are merged into the candidate's skill profile.

### Structured Candidate Profiles

Parsed candidate information is validated and represented using Pydantic models.

A candidate profile contains:

```text
CandidateProfile
├── name
├── experience
│   ├── company
│   ├── role
│   └── years
├── skills
├── education
└── projects
```

### LangGraph Assessment Workflow

The core assessment process is implemented as a LangGraph state machine.

The graph contains five stages:

1. **Profile Analyzer**
2. **Technical Interviewer**
3. **Behavioral Interviewer**
4. **Evaluation**
5. **HR Handoff**

The evaluation stage calculates an overall score from the technical and behavioral scores.

Candidates with an overall score of **15 or higher** receive a `Strong Hire` recommendation. Candidates below that threshold are marked as `Needs Review` and routed to the HR handoff stage.

### AI-Powered Conversational Interview

The platform also provides a real-time conversational assessment.

The `ChatAssessmentAgent` uses Google's Gemini API and the `gemini-2.5-flash-lite` model to generate interview questions.

The agent:

* Receives candidate responses
* Maintains conversation history
* Uses the candidate's profile as context
* Generates exactly one interview question at a time
* Limits the assessment to two generated interview questions
* Marks the assessment as complete when the question limit is reached

### Real-Time WebSocket Communication

The conversational assessment is exposed through:

```text
/ws/chat/{candidate_id}
```

The WebSocket connection:

1. Validates the candidate
2. Creates an interview state
3. Starts the conversational assessment
4. Receives candidate messages
5. Passes them to the AI interviewer
6. Returns the generated response
7. Persists the current session state

### HR Escalation

The assessment workflow can automatically flag candidates for manual HR review.

When the overall assessment score falls below the configured threshold, the `HRHandoffAgent` adds an escalation event to the interview history.

## Architecture

The backend is organized into separate layers for API handling, candidate ingestion, agent logic, workflow orchestration, configuration, and data models.

```text
backend/
├── app/
│   ├── agents/
│   │   ├── behavioral_interviewer_agent.py
│   │   ├── chat_assessment_agent.py
│   │   ├── evaluation_agent.py
│   │   ├── hr_handoff_agent.py
│   │   ├── profile_analyzer_agent.py
│   │   └── technical_interviewer_agent.py
│   │
│   ├── api/
│   │   ├── candidate.py
│   │   ├── chat.py
│   │   ├── hr.py
│   │   └── ws.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── ingestion/
│   │   ├── github.py
│   │   └── resume_parser.py
│   │
│   ├── kb/
│   │   └── knowledge_base.py
│   │
│   ├── langgraph/
│   │   ├── engine.py
│   │   ├── session_store.py
│   │   └── state.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   └── main.py
│
└── requirements.txt
```

## Technology Stack

| Component               | Technology                    |
| ----------------------- | ----------------------------- |
| API framework           | FastAPI                       |
| ASGI server             | Uvicorn                       |
| Data validation         | Pydantic                      |
| Workflow orchestration  | LangGraph                     |
| LLM                     | Google Gemini 2.5 Flash-Lite  |
| Resume parsing          | pdfplumber                    |
| GitHub integration      | GitHub REST API               |
| HTTP client             | Requests                      |
| Real-time communication | WebSockets                    |
| Configuration           | Pydantic Settings + `.env`    |
| Session storage         | In-memory Python dictionaries |

## API

### Health Check

```http
GET /health
```

Returns:

```json
{
  "status": "ok"
}
```

### Candidate Ingestion

```http
POST /candidate/ingest
```

Accepts:

* `resume_file`: PDF resume
* `github_url`: optional GitHub profile URL

Example request:

```bash
curl -X POST "http://localhost:8000/candidate/ingest" \
  -F "resume_file=@resume.pdf" \
  -F "github_url=https://github.com/username"
```

Example response:

```json
{
  "candidate_id": "generated-candidate-id",
  "profile": {
    "name": "Candidate Name",
    "experience": [],
    "skills": [],
    "education": "University",
    "projects": []
  }
}
```

The returned `candidate_id` is used for subsequent assessment operations.

### Run Candidate Assessment

```http
POST /candidate/assess?candidate_id={candidate_id}
```

This runs the candidate through the LangGraph assessment workflow.

The response contains:

* Candidate name
* Technical score
* Behavioral score
* Overall assessment report
* HR escalation status
* Projects identified from the resume

Example structure:

```json
{
  "candidate_name": "Candidate Name",
  "technical_score": 20.0,
  "behavioral_score": 15.0,
  "final_report": {
    "technical_score": 20.0,
    "behavioral_score": 15.0,
    "overall_score": 17.5,
    "recommendation": "Strong Hire"
  },
  "requires_hr": false,
  "projects_reviewed": []
}
```

### Conversational Assessment

Connect to:

```text
ws://localhost:8000/ws/chat/{candidate_id}
```

Once connected, the server starts the assessment and sends:

```text
Chat-based assessment started. Tell me about yourself.
```

Candidate responses are sent as WebSocket text messages.

The AI interviewer generates the next interview question based on the candidate profile and conversation history.

After the configured question limit is reached, the session is closed.

## Assessment Workflow

The LangGraph engine defines the assessment as a stateful workflow.

```text
                    ┌──────────────────┐
                    │ Profile Analyzer │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Technical Interview │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Behavioral Interview│
                  └──────────┬──────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │  Evaluation  │
                     └───────┬──────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
          overall >= 15            overall < 15
                 │                       │
                 ▼                       ▼
          ┌────────────┐          ┌─────────────┐
          │ Final Report│         │ HR Handoff  │
          └────────────┘          └─────────────┘
```

The workflow state tracks:

```text
candidate_id
candidate_profile
chat_history
technical_score
behavioral_score
final_report
requires_hr
```

## Scoring

The current implementation uses a simple deterministic scoring model.

### Profile Analysis

The initial technical score is calculated from the number of recognized skills:

```text
technical_score = number_of_skills × 1.5
```

The initial behavioral score is:

```text
behavioral_score = 5.0
```

### Technical Interview

The technical interviewer adds:

```text
+10 technical points
```

### Behavioral Interview

The behavioral interviewer adds:

```text
+10 behavioral points
```

### Final Evaluation

The overall score is calculated as:

```text
overall_score = (technical_score + behavioral_score) / 2
```

The current recommendation threshold is:

```text
overall_score >= 15  → Strong Hire
overall_score < 15   → Needs Review
```

Candidates requiring additional review are passed to the HR handoff stage.

## Resume Parsing

The resume parser currently works with PDF files and extracts text page by page.

It recognizes a predefined set of skills:

```text
Python
Java
C++
FastAPI
GitHub
SQL
JavaScript
TypeScript
HTML
CSS
```

Experience entries are detected using role-related keywords such as:

```text
Engineer
Developer
Manager
Intern
AI
Software
```

Project names are extracted from the project's section of the resume, with up to five projects retained.

The parser is intentionally lightweight and rule-based rather than relying on an LLM for initial resume extraction.

## GitHub Enrichment

The GitHub integration uses the public GitHub REST API.

For a supplied username, the backend retrieves the user's profile and repositories and derives:

```text
username
public_repos
followers
top_languages
stars
```

The detected repository languages are added to the candidate's skills.

## Conversational AI

The chat assessment uses Google's Generative AI SDK.

The model is initialized as:

```text
gemini-2.5-flash-lite
```

The model receives:

* Candidate name
* Candidate skills
* Candidate experience
* Candidate projects
* Conversation history
* Latest candidate response

The prompt instructs the model to return exactly one interview question without additional explanations.

The current conversational assessment is intentionally limited to two generated questions.

## Configuration

Create a `.env` file inside the `backend` directory:

```env
GOOGLE_API_KEY=your_google_api_key
```

The backend also supports the following configuration values:

```env
ENV=development
DEBUG=True
GITHUB_API_BASE=https://api.github.com
```

`GITHUB_API_BASE` defaults to the official GitHub API endpoint when it is not explicitly configured.

## Installation

### Prerequisites

* Python 3.10+
* pip
* Google Gemini API key

Clone the repository:

```bash
git clone https://github.com/Manahil-04/AI-powered-Candidate-Assessment-Platform.git
cd AI-powered-Candidate-Assessment-Platform/backend
```

Create and activate a virtual environment.

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies listed in the repository:

```bash
pip install -r requirements.txt
```

The current implementation also imports packages for LangGraph, PDF parsing, Google Generative AI, environment configuration, multipart file uploads, and Pydantic settings. If they are not already available in your environment, install them with:

```bash
pip install langgraph pdfplumber google-generativeai python-dotenv pydantic-settings python-multipart
```

Create the environment file:

```bash
cp .env.example .env
```

If an `.env.example` file is not present, create `.env` manually and add your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key
```

## Running the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI's interactive documentation is available at:

```text
http://localhost:8000/docs
```

Alternative ReDoc documentation:

```text
http://localhost:8000/redoc
```

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Typical Usage Flow

### 1. Upload a Candidate Resume

Send a PDF resume to:

```text
POST /candidate/ingest
```

Optionally include the candidate's GitHub profile.

### 2. Receive Candidate ID

The backend generates a UUID for the candidate and stores the parsed profile in memory.

### 3. Run Automated Assessment

Use the generated candidate ID with:

```text
POST /candidate/assess
```

The candidate is processed through the LangGraph workflow.

### 4. Start Conversational Assessment

Open:

```text
/ws/chat/{candidate_id}
```

The candidate can then interact with the AI interviewer in real time.

### 5. Review the Assessment

The final assessment contains technical and behavioral scores, an overall score, a hiring recommendation, and whether HR review is required.

## Data Storage

The current implementation uses in-memory storage.

Candidate profiles are held in:

```python
candidate_cache = {}
```

Chat sessions are held in:

```python
SESSION_STORE = {}
```

The knowledge-base module also maintains an in-memory candidate store.

This makes the project straightforward to run locally, but the current storage layer is not persistent. Restarting the application clears candidate profiles and interview sessions.

For a production deployment, these stores should be replaced with a persistent database and, for active sessions, a shared session store such as Redis.

## Project Design

The backend separates the major responsibilities of the assessment system:

**API layer**

Handles HTTP and WebSocket communication.

**Ingestion layer**

Converts external candidate information into structured data.

**Agent layer**

Contains the individual assessment agents.

**LangGraph layer**

Coordinates agents and maintains assessment state.

**Models layer**

Defines validated candidate data structures.

**Core layer**

Handles configuration and logging.

**Knowledge base**

Provides an abstraction for storing candidate assessment information.

This separation makes it possible to replace individual components without redesigning the complete assessment pipeline.

## Current Limitations

The current repository is an early implementation of the assessment architecture. Some components are intentionally lightweight.

### In-memory storage

Candidate profiles and sessions are lost when the server restarts.

### Rule-based resume parsing

Resume extraction currently relies on PDF text extraction, regular expressions, and a predefined skills list rather than a more sophisticated NLP or LLM-based parser.

### Simplified interview agents

The technical and behavioral interviewer agents currently modify scores directly rather than conducting independent AI-driven interviews.

### Limited conversational assessment

The Gemini-powered conversational interviewer currently generates only two questions per session.

### Basic scoring model

The scoring logic is deterministic and currently uses fixed score increments and a single hiring threshold.

### GitHub API handling

GitHub data is retrieved from public endpoints and is used primarily to augment the candidate's detected skills.

## Future Improvements

The architecture provides a foundation for expanding the assessment engine with:

* Persistent candidate and assessment storage
* More robust resume parsing
* LLM-based resume understanding
* Dynamic technical questioning
* Adaptive behavioral interviews
* Role-specific assessment criteria
* Job-description-aware candidate evaluation
* Evidence-based scoring
* Interview transcript analysis
* Recruiter dashboards
* Candidate comparison
* Redis-backed session management
* Background processing for expensive AI operations
* Authentication and authorization
* Production-grade GitHub API caching
* Automated assessment reports
* Human-in-the-loop review workflows

## Development

The application uses FastAPI's application factory pattern:

```python
def create_app() -> FastAPI:
    ...
```

The main application registers the candidate and WebSocket routers and exposes a health endpoint.

For development, run:

```bash
uvicorn app.main:app --reload
```

## License

No license is currently specified in the repository.

If you intend to distribute or accept contributions to this project, add an appropriate open-source license to the repository.

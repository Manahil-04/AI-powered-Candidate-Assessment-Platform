# AI-Powered Candidate Assessment Platform

An AI-powered candidate assessment backend built with **FastAPI, LangGraph, and Google Gemini**.

The platform currently supports resume ingestion, candidate profile extraction, optional GitHub enrichment, LangGraph-based assessment orchestration, and a real-time Gemini-powered conversational interview over WebSockets.

> **Current status:** This is an active prototype. The core assessment workflow and conversational AI infrastructure are implemented, while technical/behavioral answer evaluation, persistent storage, and recruiter-facing functionality are still under development.

## Features

### Implemented

* PDF resume upload and text extraction
* Basic resume parsing
* Structured candidate profiles using Pydantic
* Optional GitHub profile enrichment
* LangGraph assessment workflow
* Gemini-powered conversational interviewer
* Real-time WebSocket interview
* In-memory interview sessions
* Automated scoring and hiring recommendation
* HR review flagging
* Basic final assessment report
* FastAPI REST API

### Partially Implemented

* Resume intelligence

  * Extracts name, experience, skills, education, and projects
  * Currently relies on rule-based parsing and a limited skill list
* GitHub analysis

  * Retrieves repositories, followers, languages, and stars
  * Currently provides basic profile enrichment rather than deeper code analysis
* Profile analysis

  * Candidate skills influence the initial score
  * Current scoring is deterministic
* Conversational assessment

  * Gemini generates candidate-specific questions
  * Currently limited to two questions
  * Not yet connected to the main technical/behavioral scoring pipeline
* Assessment scoring

  * Overall scoring and recommendation work
  * Technical and behavioral scores currently contain fixed scoring logic
* HR handoff

  * Candidates can be flagged for HR review
  * No external HR notification or dashboard yet
* Session management

  * Works during runtime
  * Currently stored in memory

### Not Yet Implemented

* AI-based technical answer evaluation
* AI-based behavioral answer evaluation
* Adaptive technical interviews
* Adaptive behavioral interviews
* Persistent database
* Authentication and authorization
* Recruiter dashboard
* Candidate comparison
* Automated HR notifications
* Production-grade distributed session management

---

## Architecture

The current backend consists of two main flows.

### Candidate Assessment Flow

```text
Resume PDF
    │
    ▼
Resume Parser
    │
    ├──────────────► GitHub Enrichment
    │
    ▼
Candidate Profile
    │
    ▼
LangGraph Assessment
    │
    ├── Profile Analysis
    │
    ├── Technical Assessment
    │
    ├── Behavioral Assessment
    │
    └── Evaluation
             │
        ┌────┴────┐
        ▼         ▼
   Strong Hire  Needs Review
                    │
                    ▼
               HR Handoff
```

### Conversational Interview Flow

```text
Candidate
    │
    │ WebSocket
    ▼
FastAPI
    │
    ▼
Chat Assessment Agent
    │
    ▼
Google Gemini
    │
    ▼
Candidate-specific question
```

---

## Technology Stack

| Component               | Technology                   |
| ----------------------- | ---------------------------- |
| Backend                 | FastAPI                      |
| ASGI Server             | Uvicorn                      |
| Workflow                | LangGraph                    |
| LLM                     | Google Gemini 2.5 Flash-Lite |
| PDF Processing          | pdfplumber                   |
| GitHub Integration      | GitHub REST API              |
| Validation              | Pydantic                     |
| Configuration           | Pydantic Settings / `.env`   |
| Real-time Communication | WebSockets                   |
| Current Storage         | In-memory                    |

---

## Project Structure

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

---

## Assessment Workflow

The assessment workflow is orchestrated using LangGraph.

```text
Profile Analyzer
       │
       ▼
Technical Interviewer
       │
       ▼
Behavioral Interviewer
       │
       ▼
Evaluation
       │
       ├──────────────► Strong Hire
       │
       └──────────────► HR Handoff
```

The workflow maintains state including:

```text
candidate_id
candidate_profile
chat_history
technical_score
behavioral_score
final_report
requires_hr
```

### Current Assessment Logic

The current implementation uses simplified deterministic scoring.

The profile analyzer initializes the technical score based on the number of recognized skills and assigns an initial behavioral score.

The technical and behavioral assessment nodes currently add fixed points rather than evaluating candidate answers.

The final score is calculated as:

```text
overall_score = (technical_score + behavioral_score) / 2
```

The current recommendation threshold is:

```text
overall_score >= 15  → Strong Hire
overall_score < 15   → Needs Review
```

Candidates below the threshold are routed to the HR handoff stage.

---

## Resume Processing

The candidate ingestion endpoint accepts a PDF resume.

The parser extracts:

* Candidate name
* Work experience
* Skills
* Education
* Projects

The current implementation uses `pdfplumber` for PDF text extraction and rule-based parsing for identifying sections and skills.

The currently recognized skills include:

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

This parser is intentionally lightweight and is one of the areas planned for improvement.

---

## GitHub Enrichment

Candidates can optionally provide a GitHub profile URL.

The backend uses the public GitHub API to retrieve information including:

* Username
* Public repository count
* Followers
* Repository languages
* Repository stars

Detected programming languages are added to the candidate's skill profile.

This currently provides basic GitHub enrichment rather than detailed repository or code-quality analysis.

---

## AI Conversational Interview

The conversational interviewer is the primary LLM-powered component currently implemented.

It uses:

```text
Google Gemini 2.5 Flash-Lite
```

The model receives candidate-specific information including:

* Name
* Skills
* Experience
* Projects
* Conversation history
* Candidate responses

It then generates the next interview question.

The current implementation limits the conversation to **two generated questions**.

The conversational interviewer is currently separate from the deterministic technical/behavioral assessment nodes in the main LangGraph workflow.

---

## WebSocket API

Real-time interviewing is exposed through:

```text
/ws/chat/{candidate_id}
```

The WebSocket flow is:

```text
Connect
   ↓
Validate candidate
   ↓
Create interview session
   ↓
Start assessment
   ↓
Receive candidate response
   ↓
Send to Gemini
   ↓
Generate next question
   ↓
Return response
   ↓
Repeat until assessment completes
```

Interview sessions are currently maintained in memory.

---

## REST API

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

Example:

```bash
curl -X POST "http://localhost:8000/candidate/ingest" \
  -F "resume_file=@resume.pdf" \
  -F "github_url=https://github.com/username"
```

The endpoint returns a generated candidate ID and parsed profile.

### Run Assessment

```http
POST /candidate/assess?candidate_id={candidate_id}
```

Runs the candidate through the LangGraph assessment workflow and returns the assessment result.

### WebSocket Interview

```text
ws://localhost:8000/ws/chat/{candidate_id}
```

Starts the real-time conversational assessment.

---

## Setup

### Requirements

* Python 3.10+
* pip
* Google Gemini API key

Clone the repository:

```bash
git clone https://github.com/Manahil-04/AI-powered-Candidate-Assessment-Platform.git
cd AI-powered-Candidate-Assessment-Platform/backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The application also imports packages for PDF parsing, LangGraph, Gemini, environment configuration, and multipart form handling. Install any missing packages required by the current implementation:

```bash
pip install langgraph pdfplumber google-generativeai python-dotenv pydantic-settings python-multipart
```

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
```

---

## Running the Application

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Test the server:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Current Limitations

The project is currently a prototype and has several areas intentionally left for future development.

### Storage

Candidate profiles and interview sessions are stored in memory. All data is lost when the application restarts.

### Resume Understanding

Resume parsing is rule-based and currently supports a limited set of recognized skills.

### Technical and Behavioral Assessment

The LangGraph nodes exist and are connected, but they currently use simplified fixed scoring rather than actual candidate questioning and answer evaluation.

### Conversational Assessment

The Gemini interviewer is functional but currently limited to two questions and is not yet used to determine the technical or behavioral score.

### HR Workflow

HR escalation is represented internally in the assessment state. There is currently no external HR system, email notification, or recruiter dashboard.

---

## Roadmap

The next development stages can build on the existing architecture by adding:

* LLM-powered resume analysis
* Job-description-aware assessment
* Dynamic technical questioning
* Dynamic behavioral questioning
* Candidate answer evaluation
* Evidence-based scoring
* Adaptive interview difficulty
* Persistent PostgreSQL storage
* Redis-backed sessions
* Authentication and authorization
* Recruiter dashboard
* Candidate comparison
* Automated HR notifications
* Detailed assessment reports
* Production deployment and monitoring

---

## Project Status

| Area                  | Status             |
| --------------------- | ------------------ |
| Resume ingestion      | ✅ Implemented      |
| Basic resume parsing  | 🟡 Partial         |
| Candidate profiles    | ✅ Implemented      |
| GitHub enrichment     | 🟡 Partial         |
| LangGraph workflow    | ✅ Implemented      |
| Profile analysis      | 🟡 Partial         |
| Technical assessment  | 🔴 Prototype       |
| Behavioral assessment | 🔴 Prototype       |
| Gemini interviewer    | 🟡 Partial         |
| WebSocket interview   | ✅ Implemented      |
| Scoring               | 🟡 Partial         |
| Hiring recommendation | ✅ Implemented      |
| HR handoff            | 🟡 Partial         |
| Persistent storage    | 🔴 Not implemented |
| Authentication        | 🔴 Not implemented |
| Recruiter dashboard   | 🔴 Not implemented |
| AI answer evaluation  | 🔴 Not implemented |
| Adaptive interviews   | 🔴 Not implemented |


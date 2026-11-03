# HireAI — Intelligent Recruitment & Technical Assessment Platform

**HireAI** is an enterprise-grade AI technical recruitment platform combining automated resume screening, job description matching, skill-gap analysis, live coding assessments with isolated execution workers, and an AI interviewer copilot.

---

## 🎯 Features

1. **AI Resume Analyzer (Prompt 03)**:
   - Upload PDF, DOCX, and TXT resumes.
   - Extracts contact details, technical and soft skills, education, experience, and projects.
   - Identifies missing information and generates tailored improvement tips.
   - Generates structured JSON conforming to the industry schema.

2. **Job Description Analyzer (Prompt 04)**:
   - Upload or paste Job Descriptions.
   - Extracts required skills, mandatory vs. optional qualifications, and experience level.
   - Identifies programming languages, frameworks, and database requirements.

3. **AI Resume vs JD Matching Engine (Prompt 05)**:
   - Compares candidate profiles against job postings using a transparent 100-point scoring engine.
   - Category breakdowns: Python, SQL, Machine Learning, Generative AI, Communication, Overall Match.
   - Highlighting exact matches, partial semantic matches, and missing qualifications.

4. **Skill Gap Analysis & Roadmap (Prompt 06)**:
   - Identifies demonstrated skills vs. missing competencies.
   - Generates personalized beginner, intermediate, and advanced learning roadmaps.
   - Recommends hands-on practical projects to bridge detected skill gaps.

5. **Technical Assessment Platform (Prompt 07)**:
   - Supported languages: **Python, JavaScript (Node.js), C++, Java**.
   - Monaco-style interactive code editor.
   - Multiple test cases (public and hidden).
   - Isolated execution subprocess workers with CPU timeouts (5s) and peak memory telemetry.
   - Automated scoring, pass/fail badges, and submission history.

6. **AI Interviewer Copilot (Prompt 08)**:
   - Dynamically generates technical interview questions by topic (Python, SQL, ML, GenAI) and difficulty (Basic, Intermediate, Advanced).
   - Generates follow-up interview prompts for deep-dives.
   - Live Coding Error Explainer: converts runtime/syntax errors into pedagogical hints for interviewers.
   - Structured candidate scorecard and evidence-grounded summary generation.

7. **Authentication & Security (Prompt 09 & 10)**:
   - JWT-based authentication with role-based access (Recruiter, Interviewer, Candidate).
   - Zero-external-dependency RFC 7519 JWT implementation.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Lucide React, Framer Motion |
| **Backend** | Python 3.11+ / FastAPI, Pydantic v2 |
| **Database & ORM** | PostgreSQL / SQLite (zero-config local dev), SQLAlchemy 2.0 |
| **Document Processing** | PyMuPDF (PDF), python-docx (DOCX), striprtf (RTF) |
| **AI / NLP** | Sentence Transformers (`all-MiniLM-L6-v2`), spaCy |
| **Execution Workers** | Isolated Subprocess Runner / Docker Containers |
| **Deployment** | Docker & Docker Compose |

---

## 🚀 How to Run

### Method 1: Standalone Single `.exe` File (Shareable With Anyone)

You can share the standalone executable with any user on Windows without them needing Python, Node.js, or external tools:

1. Locate the built executable in the **`dist`** directory:
   ```text
   dist/HireAI.exe
   ```
2. Double-click **`HireAI.exe`**.
3. It will automatically initialize the local storage database, boot the server, and open the platform in the default browser at `http://127.0.0.1:8000/`.
4. To rebuild the `.exe` at any time, simply run:
   ```cmd
   build_exe.bat
   ```

---

### Method 2: Quick Start (Developer Python Runner)

1. Double-click **`start.bat`** in the project folder, or run:
   ```cmd
   start.bat
   ```
2. Or run directly with Python:
   ```bash
   python run.py
   ```
   *This automatically initializes database tables, boots the FastAPI server on `http://127.0.0.1:8000`, and opens the interactive HireAI dashboard in your default browser.*

---

### Method 2: PowerShell Runner

In PowerShell:
```powershell
.\run.ps1
```

---

### Method 3: Running Automated Test Suites

To run all 19 unit and integration tests (verifying parsers, matching, isolated code runner, AI copilot, and auth):

- **Command Prompt**:
  ```cmd
  test.bat
  ```
- **PowerShell**:
  ```powershell
  .\test.ps1
  ```
- **Direct Pytest**:
  ```bash
  backend\.venv\Scripts\python.exe -m pytest backend/tests -v -p no:asyncio
  ```

---

### Method 4: Production Docker Compose

Run the full stack with PostgreSQL and Redis:
```bash
docker-compose up --build
```
- Web Application: `http://localhost:3000`
- API & Interactive UI: `http://localhost:8000`
- Swagger API Documentation: `http://localhost:8000/docs`

---

## 📁 Repository Structure

```text
HireAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/               # Versioned REST APIs (Assessment, Copilot, Matching, etc.)
│   │   ├── core/                 # Config, JWT authentication, and exception handlers
│   │   ├── models/               # SQLAlchemy models (Resumes, Jobs, Questions, Submissions)
│   │   ├── schemas/              # Pydantic v2 schemas
│   │   ├── assessment/           # Question bank and assessment service
│   │   ├── interview/            # AI Interviewer Copilot engine
│   │   ├── workers/              # Isolated code runner workers
│   │   ├── ai_engine/            # NLP skill extractor & matching engine
│   │   ├── database/             # SQLite & PostgreSQL connection pooling
│   │   ├── static/               # Interactive web app & assets
│   │   └── main.py               # FastAPI application entry point
│   ├── tests/                    # 19 automated unit & integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/                      # React 18 + TypeScript SaaS application
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml            # Multi-container orchestration (DB, Redis, API, UI)
├── .env.example
├── run.py                        # Unified application launcher
├── start.bat                     # Windows CMD launcher
├── run.ps1                       # Windows PowerShell launcher
├── test.bat                      # Automated test runner
└── README.md
```

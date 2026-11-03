# Phased Development Plan — AI Career Intelligence

**Application:** AI Career Intelligence  
**Objective:** Deliver a production-grade, local-first Windows Desktop Application.  
**Execution Philosophy:** Sequential milestones, decoupled architecture, verifiable deliverables at each gate.

---

## Roadmap Overview

```
Phase 1: Architecture & Structural Scaffolding
   |
Phase 2: FastAPI Backend Core & SQLite Database Engine
   |
Phase 3: Resume Upload System & Multi-Format Document Processing
   |
Phase 4: Job Description Intelligence & Requirement Classifier
   |
Phase 5: Resume & Job Semantic Matching & 100-Point Scoring Engine
   |
Phase 6: AI Career Intelligence & Gap Recommendation Engine
   |
Phase 7: Desktop Frontend Development (React + Tauri 2)
   |
Phase 8: Full-Stack Integration & End-to-End API Pipelines
   |
Phase 9: Comprehensive Security Audit & Automated Testing
   |
Phase 10: Windows Desktop Packaging & Installer Generation
```

---

## Detailed Implementation Phases

### Phase 1: Project Architecture & Scaffolding (Current Phase)
- **Goal**: Initialize the complete file structure, documentation, and technical foundations.
- **Key Deliverables**:
  - `docs/architecture.md`, `docs/development_plan.md`, `docs/database_schema.md`, `docs/api_documentation.md`
  - Scaffolding of `frontend/`, `backend/`, `storage/`, and root files.
  - Zero code deletion; strict boundary separation between frontend and backend.
- **Gate Criteria**: All folders and documentation artifacts exist and pass architectural verification.

---

### Phase 2: Backend Development & Database Engine
- **Goal**: Build the FastAPI microservice and SQLAlchemy 2.0 SQLite persistence layer.
- **Key Deliverables**:
  - FastAPI application setup with versioned routes (`/api/v1`), CORS, custom exception handlers, and structured logging.
  - SQLite configuration with Write-Ahead Logging (`WAL`), connection pool, and foreign key enforcement.
  - 10 SQLAlchemy ORM models:
    1. `Resume`
    2. `ResumeInformation`
    3. `ResumeSkills`
    4. `JobDescription`
    5. `JobRequirements`
    6. `JobMatchAnalysis`
    7. `SkillComparison`
    8. `Recommendations`
    9. `AnalysisHistory`
    10. `ApplicationSettings`
  - Repository layer isolating SQL queries from business logic.
  - Health check endpoint `GET /api/v1/health`.
- **Gate Criteria**: Backend boots on `http://127.0.0.1:8000`, Swagger UI loads at `/docs`, and Pytest database tests pass.

---

### Phase 3: Resume Upload & Document Processing Engine
- **Goal**: Support robust multi-format document ingestion, text extraction, and candidate entity recognition.
- **Key Deliverables**:
  - `POST /api/v1/resumes/upload` with validation (MIME-type check, size limit, UUID generation).
  - Modular document parsers:
    - `pdf_parser.py` (PyMuPDF)
    - `docx_parser.py` (python-docx)
    - `doc_parser.py` (LibreOffice conversion)
    - `txt_parser.py` / `rtf_parser.py` (striprtf & encoding detection)
    - `ocr_engine.py` (Tesseract OCR fallback for scanned documents)
  - AI Information Extractor:
    - Contact information (name, email, phone, location)
    - Work experience, education, projects, certifications
    - Technical skills taxonomy (languages, frameworks, databases, cloud, DevOps, AI/ML)
- **Gate Criteria**: Sample PDF, DOCX, TXT, and RTF resumes successfully upload, extract text, and populate database entities without data loss.

---

### Phase 4: Job Description Intelligence
- **Goal**: Parse and analyze complex job descriptions into structured requirement taxonomies.
- **Key Deliverables**:
  - `POST /api/v1/jobs/analyze` and CRUD endpoints for job descriptions.
  - Support for raw text pasting and multi-format document upload (PDF, DOCX, TXT).
  - NLP Requirement Classifier:
    - Mandatory skills (explicitly required)
    - Preferred skills (desirable/nice-to-have)
    - Optional/bonus skills
    - Years of experience and degree requirements
    - Responsibilities & soft skills
  - Verifiable citation extraction (retaining exact supporting excerpts).
- **Gate Criteria**: Job descriptions are analyzed and classified with 100% evidentiary text references.

---

### Phase 5: Semantic Matching & 100-Point Scoring Engine
- **Goal**: Evaluate candidate resume alignment against job requirements with deterministic transparency.
- **Key Deliverables**:
  - Skill comparison engine (`matching_engine.py`):
    - Categorization: *Matched*, *Partially Matched*, *Missing*, *Not Verifiable*.
    - Semantic similarity via Sentence Transformers (`all-MiniLM-L6-v2`) with threshold guards.
  - Transparent 100-point scoring engine (`scoring_engine.py`):
    - Mandatory Technical Skills: 40%
    - Preferred Skills: 15%
    - Experience Alignment: 15%
    - Education Alignment: 10%
    - Practical Projects: 10%
    - Responsibilities: 5%
    - Soft Skills: 5%
  - Configurable weight adjustments stored in `ApplicationSettings`.
  - Eligibility engine determining qualification status.
- **Gate Criteria**: Deterministic calculation across test cases with mathematical verification unit tests.

---

### Phase 6: AI Career Intelligence & Recommendations
- **Goal**: Produce actionable, evidence-based career development guidance.
- **Key Deliverables**:
  - Skills gap prioritization: High (missing mandatory), Medium (partial/preferred), Low (optional).
  - Personalized learning roadmaps with recommended topics.
  - Portfolio project suggestions designed to bridge identified technical gaps.
  - Resume bullet improvement suggestions with before/after guidance.
  - Interview preparation question sets grounded in specific job requirements.
- **Gate Criteria**: Generated recommendations are directly linked to identified missing requirements.

---

### Phase 7: Desktop Frontend Development (React + Tauri 2)
- **Goal**: Create a desktop-first user interface with a design aesthetic inspired by Linear and Raycast.
- **Key Deliverables**:
  - Tauri 2 + Vite + React + TypeScript setup with Tailwind CSS and shadcn/ui.
  - App navigation & 9 core screens:
    1. Dashboard
    2. Resume Analyzer
    3. Resume Library
    4. Job Intelligence
    5. Job Matcher
    6. Skills Gap Analysis
    7. AI Career Recommendations
    8. Analysis History & Report Viewer
    9. Settings & Score Weights
  - Recharts visual components (donut score charts, skill coverage comparison bars).
  - Dark / Light mode toggle.
- **Gate Criteria**: Frontend builds cleanly with zero TypeScript errors and renders responsive desktop views.

---

### Phase 8: Full-Stack Integration & API Pipeline
- **Goal**: Connect React frontend with FastAPI backend over localhost REST endpoints.
- **Key Deliverables**:
  - Axios service layer (`resumeService.ts`, `jobService.ts`, `matchingService.ts`, etc.).
  - File upload drag-and-drop integration with real upload progress tracking.
  - Interactive profile editing and user confirmation dialogs before running matches.
  - Robust offline and error-handling states (backend connection retry, error banners).
- **Gate Criteria**: Complete user flow executes seamlessly: Upload resume -> Add job -> Match -> View radar & recommendations -> Export PDF.

---

### Phase 9: Comprehensive Security Audit & Testing
- **Goal**: Verify security hardening and achieve high automated test coverage.
- **Key Deliverables**:
  - Security audit: Path traversal testing, file size and format sanitization, SQL injection prevention, safe file cleanup.
  - Backend test suite: Pytest tests for API, parsers, extractors, matching, scoring, and database operations.
  - Frontend test suite: Vitest + React Testing Library component tests.
- **Gate Criteria**: 100% of security checks pass; test suites execute cleanly without failures.

---

### Phase 10: Windows Desktop Packaging & Installer
- **Goal**: Produce a standalone Windows executable and installer (.msi / .exe).
- **Key Deliverables**:
  - Package FastAPI backend with PyInstaller.
  - Tauri 2 sidecar configuration for automated backend process lifecycle (spawn on launch, terminate on exit).
  - Port collision detection and dynamic port resolution.
  - Windows installer bundling with desktop shortcuts and application icons.
- **Gate Criteria**: Standalone installer installs and runs on a clean Windows machine without requiring external Python or Node installations.

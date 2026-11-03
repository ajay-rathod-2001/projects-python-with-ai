# REST API Documentation — AI Career Intelligence

**Base URL:** `http://127.0.0.1:8000/api/v1`  
**API Specification:** OpenAPI 3.1  
**Interactive Docs:** `http://127.0.0.1:8000/docs` (Swagger UI), `http://127.0.0.1:8000/redoc` (ReDoc)  

---

## 1. System & Health

### `GET /health`
Returns the operational health and version status of the local backend service.

- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "application": "AI Career Intelligence",
    "version": "1.0.0",
    "environment": "desktop-local"
  }
  ```

---

## 2. Resumes API (`/api/v1/resumes`)

### `POST /resumes/upload`
Uploads a candidate resume document (`multipart/form-data`).

- **Parameters:**
  - `file`: Binary file (`.pdf`, `.docx`, `.doc`, `.txt`, `.rtf`).
- **Validation:**
  - Max file size: 15 MB (configurable).
  - MIME-type and extension matching.
  - Rejects empty / corrupted files.
- **Response `201 Created`**:
  ```json
  {
    "id": "c71a39f0-2580-4965-b15b-9d413e14fb54",
    "original_filename": "Jane_Doe_Resume.pdf",
    "file_format": "pdf",
    "file_size": 245812,
    "upload_status": "success",
    "created_at": "2026-11-02T11:00:00Z"
  }
  ```

### `GET /resumes`
Retrieves a paginated list of all stored resumes.

- **Query Parameters:** `skip=0`, `limit=50`
- **Response `200 OK`**:
  ```json
  [
    {
      "id": "c71a39f0-2580-4965-b15b-9d413e14fb54",
      "original_filename": "Jane_Doe_Resume.pdf",
      "file_format": "pdf",
      "file_size": 245812,
      "candidate_name": "Jane Doe",
      "skills_count": 28,
      "created_at": "2026-11-02T11:00:00Z"
    }
  ]
  ```

### `GET /resumes/{resume_id}`
Returns detailed extracted resume information including contact info, work history, and parsed skills.

- **Response `200 OK`**:
  ```json
  {
    "id": "c71a39f0-2580-4965-b15b-9d413e14fb54",
    "original_filename": "Jane_Doe_Resume.pdf",
    "file_format": "pdf",
    "is_confirmed": false,
    "information": {
      "full_name": "Jane Doe",
      "email": "jane.doe@example.com",
      "phone": "+1-555-0199",
      "location": "Seattle, WA",
      "summary": "Senior Software Engineer with 7+ years building distributed cloud systems...",
      "education": [{"degree": "B.S. Computer Science", "institution": "UW", "year": "2018"}],
      "experience": [{"role": "Senior Engineer", "company": "Tech Corp", "years": "2021-Present"}]
    },
    "skills": [
      {
        "id": "8432a1df-b8a1-432d-...",
        "skill_name": "Python",
        "category": "language",
        "evidence_text": "Built asynchronous microservices in Python using FastAPI."
      }
    ]
  }
  ```

### `PUT /resumes/{resume_id}/confirm`
Updates and confirms extracted candidate information after manual user review.

- **Request Body:** JSON containing updated fields.
- **Response `200 OK`**: Updated resume details object.

### `DELETE /resumes/{resume_id}`
Permanently deletes a resume, its parsed entities, and the associated file from disk.

- **Response `200 OK`**:
  ```json
  {
    "status": "success",
    "message": "Resume and associated data successfully deleted"
  }
  ```

---

## 3. Job Descriptions API (`/api/v1/jobs`)

### `POST /jobs`
Creates a job description via raw pasted text.

- **Request Body:**
  ```json
  {
    "title": "Staff Backend Engineer",
    "company": "NextGen Systems",
    "location": "Remote",
    "raw_text": "We are looking for a Staff Backend Engineer proficient in Python, Kubernetes..."
  }
  ```
- **Response `201 Created`**: Job description metadata and ID.

### `POST /jobs/upload`
Creates a job description from an uploaded file (`.pdf`, `.docx`, `.txt`).

- **Response `201 Created`**: Job description metadata and extracted text.

### `POST /jobs/{job_id}/analyze`
Triggers NLP extraction and requirement classification on a saved job description.

- **Response `200 OK`**:
  ```json
  {
    "job_id": "99e12...",
    "title": "Staff Backend Engineer",
    "requirements": [
      {
        "id": "req-1",
        "requirement_name": "Python",
        "category": "language",
        "classification": "mandatory",
        "required_experience_years": 5.0,
        "evidence_text": "Minimum 5+ years of production experience in Python."
      },
      {
        "id": "req-2",
        "requirement_name": "Kubernetes",
        "category": "devops",
        "classification": "preferred",
        "required_experience_years": null,
        "evidence_text": "Experience with container orchestration (Kubernetes) is a strong plus."
      }
    ]
  }
  ```

### `GET /jobs`
Lists all analyzed job descriptions.

### `GET /jobs/{job_id}`
Returns job description details and classified requirements.

### `DELETE /jobs/{job_id}`
Deletes a job description and its parsed requirements.

---

## 4. Matching & Compatibility API (`/api/v1/matching`)

### `POST /matching/analyze`
Executes comprehensive semantic matching and 100-point compatibility scoring between a resume and a job description.

- **Request Body:**
  ```json
  {
    "resume_id": "c71a39f0-2580-4965-b15b-9d413e14fb54",
    "job_id": "99e12..."
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "match_analysis_id": "match-abc-123",
    "overall_match_score": 86.5,
    "category_scores": {
      "mandatory_skills": 38.0,
      "preferred_skills": 12.5,
      "experience_alignment": 15.0,
      "education_alignment": 10.0,
      "projects_practical": 6.0,
      "responsibilities": 3.0,
      "soft_skills": 2.0
    },
    "eligibility": {
      "status": "satisfied",
      "summary": "Candidate exceeds mandatory technical skill thresholds and meets years of experience requirements."
    },
    "skill_comparisons": [
      {
        "skill_name": "Python",
        "requirement_category": "mandatory",
        "match_status": "matched",
        "semantic_score": 0.96,
        "resume_evidence": "Built asynchronous microservices in Python using FastAPI.",
        "explanation": "Exact technical match supported by direct work experience evidence."
      },
      {
        "skill_name": "Kubernetes",
        "requirement_category": "preferred",
        "match_status": "partially_matched",
        "semantic_score": 0.72,
        "resume_evidence": "Configured Docker containers and basic Helm deployment charts.",
        "explanation": "Docker and Helm experience demonstrates containerization fundamentals, but explicit Kubernetes cluster administration is missing."
      }
    ]
  }
  ```

---

## 5. Career Recommendations API (`/api/v1/recommendations`)

### `GET /recommendations/{match_analysis_id}`
Retrieves prioritized career growth steps, learning roadmaps, and resume improvements.

- **Response `200 OK`**:
  ```json
  {
    "match_analysis_id": "match-abc-123",
    "learning_roadmap": [
      {
        "priority": "high",
        "target_skill": "Kubernetes",
        "title": "CKA Preparation & Cloud Native Microservices",
        "description": "Deploy a multi-node cluster using Minikube or Kind with ingress controllers and persistent volumes.",
        "rationale": "Directly resolves preferred qualification requirement for the Staff Backend role."
      }
    ],
    "project_suggestions": [
      {
        "title": "Distributed Task Queue with K8s Operator",
        "description": "Construct a custom Kubernetes operator to manage worker replicas dynamically.",
        "skills_addressed": ["Kubernetes", "Go/Python", "Distributed Systems"]
      }
    ],
    "resume_improvements": [
      {
        "section": "Experience - Tech Corp",
        "current_bullet": "Helped manage container deployments.",
        "suggested_bullet": "Orchestrated Dockerized microservice workloads and authored Helm charts, cutting deployment time by 30%."
      }
    ]
  }
  ```

---

## 6. Reports & History API (`/api/v1/reports`)

### `GET /reports/history`
Returns historical match activity for the dashboard.

### `GET /reports/{match_analysis_id}/pdf`
Generates and downloads a clean, printable PDF report containing scores, radar charts, gap analysis, and recommendations.

---

## 7. Settings API (`/api/v1/settings`)

### `GET /settings/weights`
Returns current scoring weights.

### `PUT /settings/weights`
Updates custom scoring weights (must sum to 100.0).

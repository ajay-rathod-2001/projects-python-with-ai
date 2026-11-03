"""Job Description API endpoints (Upload, Paste, Parse, List, Delete)."""

import logging
from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai_engine.job_analyzer import JobAnalyzer
from app.core.config import settings
from app.database.connection import get_db
from app.document_processor import extract_document_text
from app.models.job import JobDescription, JobRequirements

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Jobs"])
job_analyzer = JobAnalyzer()


class CreateJobRequest(BaseModel):
    """Payload for creating/pasting a job description."""
    title: str | None = None
    company: str | None = None
    location: str | None = None
    raw_text: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)):
    """Create a new job description from pasted text, analyze requirements, and persist to database."""
    raw_text = payload.raw_text.strip()
    if not raw_text or len(raw_text) < 15:
        raise HTTPException(status_code=400, detail="Job description text must contain at least 15 characters.")

    # Analyze with AI Job Analyzer
    analysis = job_analyzer.analyze_job(raw_text)

    job_id = str(uuid.uuid4())
    job = JobDescription(
        id=job_id,
        title=payload.title or analysis.get("title") or "Software Engineer",
        company=payload.company or analysis.get("company") or "Target Company",
        location=payload.location or analysis.get("location") or "Remote",
        raw_text=raw_text,
        source_type="paste",
        min_experience_years=analysis.get("min_experience_years", 2.0),
        education_level=analysis.get("education_level", "Bachelor's Degree"),
    )
    db.add(job)

    # Add Classified Requirements
    req_objects = []
    for r in analysis.get("requirements", []):
        req_rec = JobRequirements(
            job_id=job_id,
            requirement_name=r["requirement_name"],
            category=r["category"],
            classification=r["classification"],
            required_experience_years=r.get("required_experience_years"),
            evidence_text=r["evidence_text"],
            is_ambiguous=r.get("is_ambiguous", False),
        )
        db.add(req_rec)
        req_objects.append(r)

    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "min_experience_years": job.min_experience_years,
        "education_level": job.education_level,
        "requirements_count": len(req_objects),
        "requirements": req_objects,
        "created_at": job.created_at.isoformat(),
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_job_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Create a job description by uploading a document file (.pdf, .docx, .txt)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required.")

    ext = Path(file.filename).suffix.lower().lstrip(".")
    allowed_exts = [e.strip() for e in settings.ALLOWED_FILE_EXTENSIONS.split(",")]
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'.")

    settings.JOB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    job_id = str(uuid.uuid4())
    stored_path = settings.JOB_STORAGE_DIR / f"{job_id}_{Path(file.filename).name}"

    file_bytes = await file.read()
    stored_path.write_bytes(file_bytes)

    raw_text = extract_document_text(stored_path, ext)
    if not raw_text or len(raw_text) < 15:
        raw_text = file_bytes.decode("utf-8", errors="ignore")

    analysis = job_analyzer.analyze_job(raw_text)

    job = JobDescription(
        id=job_id,
        title=analysis.get("title") or Path(file.filename).stem.replace("_", " ").title(),
        company=analysis.get("company") or "Target Company",
        location=analysis.get("location") or "Remote",
        raw_text=raw_text,
        source_type="upload",
        min_experience_years=analysis.get("min_experience_years", 2.0),
        education_level=analysis.get("education_level", "Bachelor's Degree"),
    )
    db.add(job)

    req_objects = []
    for r in analysis.get("requirements", []):
        req_rec = JobRequirements(
            job_id=job_id,
            requirement_name=r["requirement_name"],
            category=r["category"],
            classification=r["classification"],
            required_experience_years=r.get("required_experience_years"),
            evidence_text=r["evidence_text"],
            is_ambiguous=r.get("is_ambiguous", False),
        )
        db.add(req_rec)
        req_objects.append(r)

    db.commit()

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "min_experience_years": job.min_experience_years,
        "education_level": job.education_level,
        "requirements_count": len(req_objects),
        "requirements": req_objects,
        "created_at": job.created_at.isoformat(),
    }


@router.get("/")
async def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve all parsed job descriptions."""
    jobs = db.query(JobDescription).order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "min_experience_years": j.min_experience_years,
            "requirements_count": len(j.requirements),
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs
    ]


@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Retrieve details and classified requirements for a specific job description."""
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id '{job_id}' not found.")

    requirements = [
        {
            "id": r.id,
            "requirement_name": r.requirement_name,
            "category": r.category,
            "classification": r.classification,
            "required_experience_years": r.required_experience_years,
            "evidence_text": r.evidence_text,
            "is_ambiguous": r.is_ambiguous,
        }
        for r in job.requirements
    ]

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "raw_text": job.raw_text,
        "min_experience_years": job.min_experience_years,
        "education_level": job.education_level,
        "requirements": requirements,
        "created_at": job.created_at.isoformat(),
    }


@router.delete("/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db)):
    """Permanently delete a job description and its requirements."""
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with id '{job_id}' not found.")

    db.delete(job)
    db.commit()
    return {"status": "success", "message": f"Job '{job_id}' deleted successfully."}

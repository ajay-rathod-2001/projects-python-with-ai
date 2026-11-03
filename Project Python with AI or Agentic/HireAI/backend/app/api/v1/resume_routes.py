"""Resume API endpoints (Upload, Manual Paste, Extraction, List, Details, Deletion)."""

import logging
from pathlib import Path
import shutil
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai_engine.skill_extractor import SkillExtractor
from app.core.config import settings
from app.database.connection import get_db
from app.document_processor import extract_document_text
from app.models.resume import Resume, ResumeInformation, ResumeSkills

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["Resumes"])
skill_extractor = SkillExtractor()


class ManualResumeRequest(BaseModel):
    """Payload for manually pasted resume text."""
    raw_text: str
    candidate_name: str | None = None
    original_filename: str | None = "manual_resume.txt"


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a candidate resume file (PDF, DOCX, DOC, TXT, RTF), extract text and skills."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename must be provided.")

    ext = Path(file.filename).suffix.lower().lstrip(".")
    allowed_exts = [e.strip() for e in settings.ALLOWED_FILE_EXTENSIONS.split(",")]
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(allowed_exts)}",
        )

    # Ensure storage directory exists
    settings.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Generate unique stored filename
    resume_id = str(uuid.uuid4())
    safe_filename = f"{resume_id}_{Path(file.filename).name}"
    stored_path = settings.RESUME_STORAGE_DIR / safe_filename

    # Save uploaded file to disk
    file_bytes = await file.read()
    if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB).",
        )
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    stored_path.write_bytes(file_bytes)

    # Extract plain text
    try:
        raw_text = extract_document_text(stored_path, ext)
    except Exception as e:
        logger.error("Failed to extract document text: %s", e)
        raw_text = ""

    if not raw_text or len(raw_text.strip()) < 10:
        # If extraction was empty, fallback to raw string decoding
        raw_text = file_bytes.decode("utf-8", errors="ignore")

    # AI Information & Skill Extraction
    extracted_info = skill_extractor.extract_candidate_info(raw_text)
    extracted_skills = skill_extractor.extract_skills(raw_text)

    # Create Database Records
    resume = Resume(
        id=resume_id,
        original_filename=file.filename,
        file_format=ext,
        file_size_bytes=len(file_bytes),
        stored_file_path=str(stored_path),
        raw_text=raw_text,
        processing_status="completed",
        is_confirmed=False,
    )
    db.add(resume)

    # Add Structured Information
    candidate_name = extracted_info.get("full_name") or Path(file.filename).stem.replace("_", " ").title()
    info_record = ResumeInformation(
        resume_id=resume_id,
        full_name=candidate_name,
        email=extracted_info.get("email"),
        phone=extracted_info.get("phone"),
        location=extracted_info.get("location"),
        summary=extracted_info.get("summary"),
        education_json=extracted_info.get("education"),
        experience_json=extracted_info.get("experience"),
        projects_json=extracted_info.get("projects"),
        certifications_json=extracted_info.get("certifications"),
    )
    db.add(info_record)

    # Add Extracted Skills
    for s in extracted_skills:
        skill_rec = ResumeSkills(
            resume_id=resume_id,
            skill_name=s["skill_name"],
            category=s["category"],
            years_of_experience=s.get("years_of_experience"),
            evidence_text=s.get("evidence_text"),
        )
        db.add(skill_rec)

    db.commit()
    db.refresh(resume)

    tech_skills = [s["skill_name"] for s in extracted_skills if s.get("category") != "soft_skill"]
    soft_skills = [s["skill_name"] for s in extracted_skills if s.get("category") == "soft_skill"]

    return {
        "id": resume.id,
        "original_filename": resume.original_filename,
        "file_format": resume.file_format,
        "file_size": resume.file_size_bytes,
        "candidate_name": candidate_name,
        "email": extracted_info.get("email"),
        "phone": extracted_info.get("phone"),
        "location": extracted_info.get("location"),
        "skills_count": len(extracted_skills),
        "skills": extracted_skills,
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "education": extracted_info.get("education", []),
        "experience": extracted_info.get("experience", []),
        "projects": extracted_info.get("projects", []),
        "certifications": extracted_info.get("certifications", []),
        "missing_information": extracted_info.get("missing_information", []),
        "upload_status": "success",
        "created_at": resume.created_at.isoformat(),
    }


@router.post("/manual", status_code=status.HTTP_201_CREATED)
async def upload_manual_resume(
    payload: ManualResumeRequest,
    db: Session = Depends(get_db),
):
    """Manually paste or input resume text directly without requiring a file upload."""
    raw_text = payload.raw_text.strip()
    if not raw_text or len(raw_text) < 20:
        raise HTTPException(status_code=400, detail="Resume text must contain at least 20 characters.")

    settings.RESUME_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    resume_id = str(uuid.uuid4())
    filename = payload.original_filename or "manual_resume.txt"
    stored_path = settings.RESUME_STORAGE_DIR / f"{resume_id}_{filename}"
    stored_path.write_text(raw_text, encoding="utf-8")

    # AI Extraction
    extracted_info = skill_extractor.extract_candidate_info(raw_text)
    extracted_skills = skill_extractor.extract_skills(raw_text)

    candidate_name = payload.candidate_name or extracted_info.get("full_name") or "Manual Candidate"

    resume = Resume(
        id=resume_id,
        original_filename=filename,
        file_format="txt",
        file_size_bytes=len(raw_text.encode("utf-8")),
        stored_file_path=str(stored_path),
        raw_text=raw_text,
        processing_status="completed",
        is_confirmed=True,
    )
    db.add(resume)

    info_record = ResumeInformation(
        resume_id=resume_id,
        full_name=candidate_name,
        email=extracted_info.get("email"),
        phone=extracted_info.get("phone"),
        location=extracted_info.get("location"),
        summary=extracted_info.get("summary"),
        education_json=extracted_info.get("education"),
        experience_json=extracted_info.get("experience"),
        projects_json=extracted_info.get("projects"),
        certifications_json=extracted_info.get("certifications"),
    )
    db.add(info_record)

    for s in extracted_skills:
        skill_rec = ResumeSkills(
            resume_id=resume_id,
            skill_name=s["skill_name"],
            category=s["category"],
            years_of_experience=s.get("years_of_experience"),
            evidence_text=s.get("evidence_text"),
        )
        db.add(skill_rec)

    db.commit()

    tech_skills = [s["skill_name"] for s in extracted_skills if s.get("category") != "soft_skill"]
    soft_skills = [s["skill_name"] for s in extracted_skills if s.get("category") == "soft_skill"]

    return {
        "id": resume.id,
        "original_filename": filename,
        "file_format": "txt",
        "file_size": resume.file_size_bytes,
        "candidate_name": candidate_name,
        "email": extracted_info.get("email"),
        "phone": extracted_info.get("phone"),
        "location": extracted_info.get("location"),
        "skills_count": len(extracted_skills),
        "skills": extracted_skills,
        "technical_skills": tech_skills,
        "soft_skills": soft_skills,
        "education": extracted_info.get("education", []),
        "experience": extracted_info.get("experience", []),
        "projects": extracted_info.get("projects", []),
        "certifications": extracted_info.get("certifications", []),
        "missing_information": extracted_info.get("missing_information", []),
        "upload_status": "success",
        "created_at": resume.created_at.isoformat(),
    }


@router.get("/")
async def list_resumes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve all uploaded candidate resumes with summary stats."""
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()
    results = []
    for r in resumes:
        cand_name = r.information.full_name if r.information else Path(r.original_filename).stem
        results.append({
            "id": r.id,
            "original_filename": r.original_filename,
            "file_format": r.file_format,
            "file_size": r.file_size_bytes,
            "candidate_name": cand_name,
            "skills_count": len(r.skills),
            "processing_status": r.processing_status,
            "created_at": r.created_at.isoformat(),
        })
    return results


@router.get("/{resume_id}")
async def get_resume(resume_id: str, db: Session = Depends(get_db)):
    """Retrieve full candidate resume information and extracted skills."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume with id '{resume_id}' not found.")

    info = {}
    if resume.information:
        info = {
            "full_name": resume.information.full_name,
            "email": resume.information.email,
            "phone": resume.information.phone,
            "location": resume.information.location,
            "summary": resume.information.summary,
            "education": resume.information.education_json or [],
            "experience": resume.information.experience_json or [],
            "projects": resume.information.projects_json or [],
            "certifications": resume.information.certifications_json or [],
        }

    skills = [
        {
            "id": s.id,
            "skill_name": s.skill_name,
            "category": s.category,
            "years_of_experience": s.years_of_experience,
            "evidence_text": s.evidence_text,
        }
        for s in resume.skills
    ]

    return {
        "id": resume.id,
        "original_filename": resume.original_filename,
        "file_format": resume.file_format,
        "is_confirmed": resume.is_confirmed,
        "raw_text": resume.raw_text,
        "information": info,
        "skills": skills,
        "created_at": resume.created_at.isoformat(),
    }


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db: Session = Depends(get_db)):
    """Permanently delete a resume record and its file from storage."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail=f"Resume with id '{resume_id}' not found.")

    # Remove file from disk
    try:
        file_path = Path(resume.stored_file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.warning("Could not delete stored file %s: %s", resume.stored_file_path, e)

    db.delete(resume)
    db.commit()

    return {"status": "success", "message": f"Resume '{resume_id}' deleted successfully."}

"""Reporting and Historical Audit API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.history import AnalysisHistory
from app.models.match import JobMatchAnalysis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/history")
async def get_analysis_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve historical match assessments for dashboard analytics."""
    records = db.query(AnalysisHistory).order_by(AnalysisHistory.analysis_date.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "match_analysis_id": r.match_analysis_id,
            "candidate_name": r.resume_name,
            "job_title": r.job_title,
            "company_name": r.company_name,
            "overall_score": r.overall_score,
            "matched_count": r.matched_count,
            "missing_count": r.missing_count,
            "date": r.analysis_date.isoformat(),
        }
        for r in records
    ]


@router.get("/{analysis_id}/summary")
async def get_analysis_summary(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve complete executive summary of an analysis."""
    analysis = db.query(JobMatchAnalysis).filter(JobMatchAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")

    return {
        "analysis_id": analysis.id,
        "resume_id": analysis.resume_id,
        "job_id": analysis.job_id,
        "overall_score": analysis.overall_match_score,
        "eligibility_status": analysis.eligibility_status,
        "eligibility_summary": analysis.eligibility_summary,
        "scores_breakdown": {
            "mandatory_skills": analysis.mandatory_skills_score,
            "preferred_skills": analysis.preferred_skills_score,
            "experience_alignment": analysis.experience_score,
            "education_alignment": analysis.education_score,
            "projects_practical": analysis.projects_score,
            "responsibilities": analysis.responsibilities_score,
            "soft_skills": analysis.soft_skills_score,
        },
        "created_at": analysis.created_at.isoformat(),
    }

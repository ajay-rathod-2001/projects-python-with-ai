"""Career Recommendation API endpoints (Roadmaps, Project Ideas, Interview Prep)."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.match import JobMatchAnalysis
from app.models.recommendation import Recommendations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/{analysis_id}")
async def get_recommendations(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve actionable learning roadmaps and portfolio project ideas for an analysis."""
    analysis = db.query(JobMatchAnalysis).filter(JobMatchAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")

    recs = db.query(Recommendations).filter(Recommendations.match_analysis_id == analysis_id).all()

    learning_paths = [
        {
            "id": r.id,
            "priority": r.priority,
            "target_skill": r.target_skill,
            "title": r.title,
            "description": r.description,
            "rationale": r.rationale,
        }
        for r in recs
        if r.type == "learning_path"
    ]

    return {
        "analysis_id": analysis_id,
        "overall_score": analysis.overall_match_score,
        "eligibility_status": analysis.eligibility_status,
        "learning_roadmap": learning_paths,
    }

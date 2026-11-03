"""FastAPI router for Technical Assessments and Coding Submissions."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.assessment.service import AssessmentService
from app.database.connection import get_db
from app.models.assessment import AssessmentQuestion
from app.schemas.assessment import (
    AssessmentQuestionCreate,
    AssessmentQuestionResponse,
    CodeExecutionResponse,
    CodeRunRequest,
    CodeSubmitRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessment", tags=["Technical Assessment"])


@router.get("/questions", response_model=List[AssessmentQuestionResponse])
def list_questions(
    category: Optional[str] = Query(None, description="coding or mcq"),
    language: Optional[str] = Query(None, description="python, javascript, etc."),
    db: Session = Depends(get_db),
):
    """Retrieve all available assessment questions and coding challenges."""
    service = AssessmentService(db)
    return service.get_all_questions(category=category, language=language)


@router.get("/questions/{question_id}")
def get_question(question_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a specific assessment question."""
    service = AssessmentService(db)
    q = service.get_question_by_id(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Assessment question not found.")

    public_cases = [tc for tc in (q.test_cases or []) if not tc.get("is_hidden", False)]
    return {
        "id": q.id,
        "title": q.title,
        "slug": q.slug,
        "category": q.category,
        "language": q.language,
        "difficulty": q.difficulty,
        "description": q.description,
        "starter_code": q.starter_code,
        "public_test_cases": public_cases,
        "total_test_cases_count": len(q.test_cases or []),
        "mcq_options": q.mcq_options,
        "tags": q.tags,
    }


@router.post("/run", response_model=CodeExecutionResponse)
def run_code_against_public_tests(payload: CodeRunRequest, db: Session = Depends(get_db)):
    """Run candidate code against public test cases with timing & memory stats."""
    service = AssessmentService(db)
    res = service.run_candidate_code(
        question_id=payload.question_id,
        code=payload.code,
        language=payload.language,
        include_hidden=False,
    )
    return res


@router.post("/submit", response_model=CodeExecutionResponse)
def submit_final_code(payload: CodeSubmitRequest, db: Session = Depends(get_db)):
    """Submit code for full evaluation against both public and hidden test cases."""
    service = AssessmentService(db)
    res = service.submit_assessment(
        question_id=payload.question_id,
        candidate_name=payload.candidate_name,
        candidate_email=payload.candidate_email or "",
        code=payload.code,
        language=payload.language,
    )
    return res


@router.get("/submissions")
def list_submissions(
    question_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List recent candidate submissions with scoring metrics."""
    service = AssessmentService(db)
    return service.get_submissions(question_id=question_id)

"""FastAPI router for AI Interviewer Copilot."""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.interview.copilot import AIInterviewerCopilot
from app.schemas.interview import (
    ExplainErrorRequest,
    ExplainErrorResponse,
    GenerateQuestionsRequest,
    InterviewSummaryResponse,
    QuestionItem,
    SummarizeInterviewRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["AI Interviewer Copilot"])
copilot = AIInterviewerCopilot()


@router.post("/generate-questions", response_model=List[QuestionItem])
def generate_questions(payload: GenerateQuestionsRequest):
    """Dynamically generate technical interview questions based on role, skills, and difficulty."""
    questions = copilot.generate_interview_questions(
        job_title=payload.job_title,
        category=payload.category,
        difficulty=payload.difficulty,
        skills=payload.skills,
        count=payload.count,
    )
    return questions


@router.post("/explain-error", response_model=ExplainErrorResponse)
def explain_coding_error(payload: ExplainErrorRequest):
    """Analyze a candidate's coding/test error and provide hints for the interviewer."""
    return copilot.explain_coding_error(
        code=payload.code,
        error_message=payload.error_message,
        language=payload.language,
    )


@router.post("/summarize", response_model=InterviewSummaryResponse)
def summarize_interview(payload: SummarizeInterviewRequest):
    """Aggregate multi-dimensional interviewer ratings into an evidence-based summary scorecard."""
    return copilot.generate_interview_summary(
        candidate_name=payload.candidate_name,
        job_title=payload.job_title,
        ratings=payload.ratings,
        notes=payload.notes or "",
        strengths=payload.strengths,
        concerns=payload.concerns,
    )

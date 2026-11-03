"""Pydantic v2 schemas for AI Interviewer Copilot."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerateQuestionsRequest(BaseModel):
    job_title: str = "Senior Software Engineer"
    category: str = "all"  # python, sql, machine_learning, generative_ai, all
    difficulty: str = "intermediate"  # basic, intermediate, advanced
    skills: Optional[List[str]] = None
    count: int = Field(5, ge=1, le=20)


class QuestionItem(BaseModel):
    category: str
    difficulty: str
    question_text: str
    ideal_answer: str
    evaluation_criteria: List[str]
    follow_up_questions: List[str]


class ExplainErrorRequest(BaseModel):
    code: str
    error_message: str
    language: str = "python"


class ExplainErrorResponse(BaseModel):
    error_summary: str
    root_cause_explanation: str
    interviewer_hint: str
    suggested_follow_up_prompt: str
    recommended_focus: str


class SummarizeInterviewRequest(BaseModel):
    candidate_name: str
    job_title: str
    ratings: Dict[str, int]  # e.g. {"algorithms": 4, "system_design": 5, "communication": 4}
    notes: Optional[str] = ""
    strengths: Optional[List[str]] = None
    concerns: Optional[List[str]] = None


class InterviewSummaryResponse(BaseModel):
    candidate_name: str
    job_title: str
    average_score: float
    recommendation: str
    executive_summary: str
    dimension_scores: Dict[str, int]
    key_strengths: List[str]
    key_concerns: List[str]
    interviewer_notes: Optional[str] = None

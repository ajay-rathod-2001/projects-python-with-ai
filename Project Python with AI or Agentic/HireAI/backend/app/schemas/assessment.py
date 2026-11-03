"""Pydantic v2 schemas for Technical Assessments."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestCaseSchema(BaseModel):
    id: int
    input: Any
    expected: Any
    is_hidden: bool = False
    explanation: Optional[str] = None


class AssessmentQuestionCreate(BaseModel):
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    description: str
    category: str = "coding"  # coding, mcq
    language: str = "python"
    difficulty: str = "medium"
    starter_code: Optional[str] = None
    solution_template: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    mcq_options: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class AssessmentQuestionResponse(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    language: str
    difficulty: str
    description: str
    starter_code: Optional[str] = None
    public_test_cases: List[Dict[str, Any]] = []
    total_test_cases_count: int = 0
    mcq_options: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None


class CodeRunRequest(BaseModel):
    question_id: str
    code: str
    language: str = "python"


class CodeSubmitRequest(BaseModel):
    question_id: str
    candidate_name: str = "Anonymous Candidate"
    candidate_email: Optional[str] = None
    code: str
    language: str = "python"


class CodeExecutionResponse(BaseModel):
    status: str
    passed_count: int
    total_count: int
    score_percentage: float
    execution_time_ms: float
    memory_used_kb: float
    test_case_results: List[Dict[str, Any]]
    output: Optional[str] = ""
    error: Optional[str] = ""
    ai_analysis: Optional[str] = None
    submission_id: Optional[str] = None
    candidate_name: Optional[str] = None

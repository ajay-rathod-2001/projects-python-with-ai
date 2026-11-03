"""SQLAlchemy ORM models for Technical Assessments and Coding Submissions."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


def generate_uuid() -> str:
    """Generate a UUID v4 string for primary keys."""
    return str(uuid.uuid4())


class AssessmentQuestion(Base):
    """Technical assessment question (Coding challenge or MCQ)."""

    __tablename__ = "assessment_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(50), default="coding", nullable=False)  # coding, mcq, system_design
    language = Column(String(50), default="python", nullable=False)  # python, javascript, java, cpp, all
    difficulty = Column(String(20), default="medium", nullable=False)  # easy, medium, hard
    time_limit_seconds = Column(Integer, default=5, nullable=False)
    memory_limit_mb = Column(Integer, default=128, nullable=False)

    starter_code = Column(Text, nullable=True)
    solution_template = Column(Text, nullable=True)

    # Test cases: [{"id": 1, "input": "...", "expected": "...", "is_hidden": false, "explanation": "..."}]
    test_cases = Column(JSON, nullable=True)

    # MCQ options: [{"id": "A", "text": "...", "is_correct": true}]
    mcq_options = Column(JSON, nullable=True)

    tags = Column(JSON, nullable=True)  # ["algorithms", "strings", "hash-map"]
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    submissions = relationship(
        "AssessmentSubmission",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class AssessmentSubmission(Base):
    """Candidate code submission and automated test execution results."""

    __tablename__ = "assessment_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(
        String(36),
        ForeignKey("assessment_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    candidate_name = Column(String(255), default="Anonymous Candidate", nullable=False)
    candidate_email = Column(String(255), nullable=True)
    language = Column(String(50), default="python", nullable=False)
    submitted_code = Column(Text, nullable=False)

    # Evaluation results
    status = Column(String(30), default="pending", nullable=False)  # passed, failed, runtime_error, timeout
    passed_count = Column(Integer, default=0, nullable=False)
    total_count = Column(Integer, default=0, nullable=False)
    score_percentage = Column(Float, default=0.0, nullable=False)
    execution_time_ms = Column(Float, default=0.0, nullable=False)
    memory_used_kb = Column(Float, default=0.0, nullable=False)

    test_case_results = Column(JSON, nullable=True)  # List of detailed test case execution statuses
    ai_analysis = Column(Text, nullable=True)  # AI code quality, time complexity analysis, improvement tips
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    question = relationship("AssessmentQuestion", back_populates="submissions")


Index("idx_assessment_questions_lang", AssessmentQuestion.language)
Index("idx_assessment_questions_diff", AssessmentQuestion.difficulty)
Index("idx_assessment_subs_qid", AssessmentSubmission.question_id)

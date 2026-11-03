"""SQLAlchemy ORM models for AI Interviewer Copilot and Interview Sessions."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
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


class InterviewSession(Base):
    """Live or planned technical interview session."""

    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    candidate_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True)

    status = Column(String(30), default="in_progress", nullable=False)  # scheduled, in_progress, completed
    overall_rating = Column(String(30), nullable=True)  # strong_hire, hire, weak_hire, no_hire
    summary = Column(Text, nullable=True)
    strengths = Column(JSON, nullable=True)  # List of demonstrated candidate strengths
    concerns = Column(JSON, nullable=True)   # List of areas needing verification or improvement
    evaluation_criteria_scores = Column(JSON, nullable=True)  # {"problem_solving": 4, "system_design": 5, ...}
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class InterviewQuestion(Base):
    """Questions dynamically generated or selected for an interview session."""

    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=True)
    category = Column(String(50), nullable=False)  # python, sql, machine_learning, generative_ai, architecture
    difficulty = Column(String(20), default="intermediate", nullable=False)  # basic, intermediate, advanced
    question_text = Column(Text, nullable=False)
    ideal_answer = Column(Text, nullable=True)
    evaluation_criteria = Column(JSON, nullable=True)  # List of criteria
    follow_up_questions = Column(JSON, nullable=True)  # List of suggested follow-up prompts

    # In-interview scoring & notes by human interviewer
    candidate_response_summary = Column(Text, nullable=True)
    interviewer_rating = Column(Integer, nullable=True)  # 1 to 5
    interviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    session = relationship("InterviewSession", back_populates="questions")


Index("idx_interview_questions_category", InterviewQuestion.category)
Index("idx_interview_questions_diff", InterviewQuestion.difficulty)

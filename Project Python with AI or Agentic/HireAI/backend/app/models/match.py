"""SQLAlchemy ORM models for JobMatchAnalysis and SkillComparison."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


def generate_uuid() -> str:
    """Generate a UUID v4 string for primary keys."""
    return str(uuid.uuid4())


class JobMatchAnalysis(Base):
    """Aggregate scoring and compatibility analysis record."""

    __tablename__ = "job_match_analyses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = Column(
        String(36),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # 100-Point Scoring Breakdown
    overall_match_score = Column(Float, nullable=False)
    mandatory_skills_score = Column(Float, nullable=False)
    preferred_skills_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    projects_score = Column(Float, nullable=False)
    responsibilities_score = Column(Float, nullable=False)
    soft_skills_score = Column(Float, nullable=False)

    eligibility_status = Column(String(30), nullable=False)  # satisfied, partially_satisfied, not_satisfied
    eligibility_summary = Column(Text, nullable=False)
    weights_applied_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    resume = relationship("Resume", back_populates="matches")
    job = relationship("JobDescription", back_populates="matches")
    comparisons = relationship(
        "SkillComparison",
        back_populates="match_analysis",
        cascade="all, delete-orphan",
    )
    recommendations = relationship(
        "Recommendations",
        back_populates="match_analysis",
        cascade="all, delete-orphan",
    )
    history_entry = relationship(
        "AnalysisHistory",
        back_populates="match_analysis",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SkillComparison(Base):
    """Fine-grained comparison between individual requirement and resume evidence."""

    __tablename__ = "skill_comparisons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_analysis_id = Column(
        String(36),
        ForeignKey("job_match_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_id = Column(
        String(36),
        ForeignKey("job_requirements.id", ondelete="SET NULL"),
        nullable=True,
    )
    skill_name = Column(String(100), nullable=False)
    match_status = Column(String(25), nullable=False)  # matched, partially_matched, missing, not_verifiable
    semantic_score = Column(Float, default=0.0, nullable=False)
    resume_evidence = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    match_analysis = relationship("JobMatchAnalysis", back_populates="comparisons")


Index("idx_skill_comparisons_analysis_id", SkillComparison.match_analysis_id)
Index("idx_skill_comparisons_skill_name", SkillComparison.skill_name)

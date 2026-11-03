"""SQLAlchemy ORM models for JobDescription and JobRequirements."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


def generate_uuid() -> str:
    """Generate a UUID v4 string for primary keys."""
    return str(uuid.uuid4())


class JobDescription(Base):
    """Job posting document record."""

    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    location = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    source_type = Column(String(20), default="paste", nullable=False)  # paste, upload
    min_experience_years = Column(Float, nullable=True)
    education_level = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    requirements = relationship(
        "JobRequirements",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    matches = relationship(
        "JobMatchAnalysis",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class JobRequirements(Base):
    """Classified requirement items extracted from job descriptions."""

    __tablename__ = "job_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(
        String(36),
        ForeignKey("job_descriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    requirement_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # technical, education, experience, soft_skill
    classification = Column(String(20), nullable=False)  # mandatory, preferred, optional, bonus
    required_experience_years = Column(Float, nullable=True)
    evidence_text = Column(Text, nullable=False)
    is_ambiguous = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    job = relationship("JobDescription", back_populates="requirements")


Index("idx_job_requirements_job_id", JobRequirements.job_id)
Index("idx_job_requirements_name", JobRequirements.requirement_name)

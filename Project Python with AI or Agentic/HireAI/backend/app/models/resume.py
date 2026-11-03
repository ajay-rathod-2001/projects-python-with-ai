"""SQLAlchemy ORM models for Resume, ResumeInformation, and ResumeSkills."""

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


class Resume(Base):
    """Uploaded candidate resume document record."""

    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    original_filename = Column(String(255), nullable=False)
    file_format = Column(String(10), nullable=False)  # pdf, docx, doc, txt, rtf
    file_size_bytes = Column(Integer, nullable=False)
    stored_file_path = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=True)
    processing_status = Column(String(20), default="pending", nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    information = relationship(
        "ResumeInformation",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
    )
    skills = relationship(
        "ResumeSkills",
        back_populates="resume",
        cascade="all, delete-orphan",
    )
    matches = relationship(
        "JobMatchAnalysis",
        back_populates="resume",
        cascade="all, delete-orphan",
    )


class ResumeInformation(Base):
    """Structured candidate personal and professional information."""

    __tablename__ = "resume_information"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)

    # Structured experience and education arrays
    education_json = Column(JSON, nullable=True)
    experience_json = Column(JSON, nullable=True)
    internships_json = Column(JSON, nullable=True)
    projects_json = Column(JSON, nullable=True)
    certifications_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume = relationship("Resume", back_populates="information")


class ResumeSkills(Base):
    """Extracted candidate skills with textual context citations."""

    __tablename__ = "resume_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(
        String(36),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # language, framework, database, cloud, devops, ai_ml, soft_skill
    years_of_experience = Column(Float, nullable=True)
    evidence_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    resume = relationship("Resume", back_populates="skills")


# Indexes for rapid skill querying
Index("idx_resume_skills_resume_id", ResumeSkills.resume_id)
Index("idx_resume_skills_skill_name", ResumeSkills.skill_name)

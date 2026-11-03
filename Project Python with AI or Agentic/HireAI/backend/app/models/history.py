"""SQLAlchemy ORM model for AnalysisHistory."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


def generate_uuid() -> str:
    """Generate a UUID v4 string for primary keys."""
    return str(uuid.uuid4())


class AnalysisHistory(Base):
    """Snapshot audit and history record for dashboard fast indexing."""

    __tablename__ = "analysis_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_analysis_id = Column(
        String(36),
        ForeignKey("job_match_analyses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    resume_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    overall_score = Column(Float, nullable=False)
    matched_count = Column(Integer, nullable=False)
    missing_count = Column(Integer, nullable=False)
    analysis_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    match_analysis = relationship("JobMatchAnalysis", back_populates="history_entry")


Index("idx_analysis_history_date", AnalysisHistory.analysis_date.desc())

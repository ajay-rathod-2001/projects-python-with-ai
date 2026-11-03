"""SQLAlchemy ORM model for Recommendations."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column,
    DateTime,
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


class Recommendations(Base):
    """Actionable career growth and learning recommendations."""

    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    match_analysis_id = Column(
        String(36),
        ForeignKey("job_match_analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    type = Column(String(50), nullable=False)  # learning_path, project_idea, resume_bullet, interview_prep
    priority = Column(String(20), nullable=False)  # high, medium, low
    target_skill = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    match_analysis = relationship("JobMatchAnalysis", back_populates="recommendations")


Index("idx_recommendations_analysis_id", Recommendations.match_analysis_id)
Index("idx_recommendations_priority", Recommendations.priority)

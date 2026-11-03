"""SQLAlchemy ORM model for ApplicationSettings."""

from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    JSON,
    String,
)

from app.database.connection import Base


class ApplicationSettings(Base):
    """Local configuration and custom scoring weights."""

    __tablename__ = "application_settings"

    key = Column(String(100), primary_key=True)
    value_json = Column(JSON, nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

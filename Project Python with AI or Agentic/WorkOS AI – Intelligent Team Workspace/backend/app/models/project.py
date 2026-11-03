import enum
from sqlalchemy import Column, String, Text, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class ProjectStatusEnum(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base, TimestampMixin):
    """Project domain entity isolated per workspace."""
    __tablename__ = "projects"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(ProjectStatusEnum, name="project_status_enum"),
        default=ProjectStatusEnum.PLANNING,
        nullable=False,
    )
    start_date = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    lead_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="projects")
    lead = relationship("User", foreign_keys=[lead_id])
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="project", cascade="all, delete-orphan")

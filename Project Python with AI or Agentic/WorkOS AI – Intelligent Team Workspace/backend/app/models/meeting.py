import enum
from sqlalchemy import Column, String, Text, Date, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class ActionItemStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


class Meeting(Base, TimestampMixin):
    """Team meeting event with summaries and AI-extracted insights."""
    __tablename__ = "meetings"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id = Column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=True
    )
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    key_decisions = Column(JSON, default=list, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="meetings")
    project = relationship("Project", back_populates="meetings")
    transcripts = relationship(
        "MeetingTranscript", back_populates="meeting", cascade="all, delete-orphan"
    )
    action_items = relationship(
        "MeetingActionItem", back_populates="meeting", cascade="all, delete-orphan"
    )


class MeetingTranscript(Base, TimestampMixin):
    """Raw audio or text transcript of a meeting session."""
    __tablename__ = "meeting_transcripts"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    meeting_id = Column(
        GUID(), ForeignKey("meetings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    raw_text = Column(Text, nullable=False)
    speaker_segments = Column(JSON, default=list, nullable=False)

    meeting = relationship("Meeting", back_populates="transcripts")


class MeetingActionItem(Base, TimestampMixin):
    """AI extracted action items awaiting human approval before converting into tasks."""
    __tablename__ = "meeting_action_items"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    meeting_id = Column(
        GUID(), ForeignKey("meetings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    action_text = Column(Text, nullable=False)
    suggested_assignee_id = Column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    suggested_due_date = Column(Date, nullable=True)
    status = Column(
        SQLEnum(ActionItemStatusEnum, name="action_item_status_enum"),
        default=ActionItemStatusEnum.PENDING,
        nullable=False,
    )
    converted_task_id = Column(
        GUID(), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )

    meeting = relationship("Meeting", back_populates="action_items")
    suggested_assignee = relationship("User", foreign_keys=[suggested_assignee_id])
    converted_task = relationship("Task", foreign_keys=[converted_task_id])

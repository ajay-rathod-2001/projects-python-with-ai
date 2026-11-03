import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class ActionStatusEnum(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class AgentActionAudit(Base, TimestampMixin):
    """Tracks and audit-logs AI agent action proposals and human approval decisions."""
    __tablename__ = "agent_action_audits"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requested_by_user_id = Column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    approved_by_user_id = Column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    intent = Column(String(255), nullable=False)
    tool_name = Column(String(100), nullable=False)
    tool_parameters = Column(JSON, default=dict, nullable=False)
    execution_result = Column(JSON, nullable=True)
    status = Column(
        SQLEnum(ActionStatusEnum, name="action_status_enum"),
        default=ActionStatusEnum.PENDING_APPROVAL,
        index=True,
        nullable=False,
    )
    executed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="action_audits")
    requested_by = relationship("User", foreign_keys=[requested_by_user_id])
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])

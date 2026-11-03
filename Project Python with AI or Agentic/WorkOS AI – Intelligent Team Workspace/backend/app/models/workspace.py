import enum
from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class WorkspaceRoleEnum(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Workspace(Base, TimestampMixin):
    """Isolated multi-tenant workspace container."""
    __tablename__ = "workspaces"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    owner_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    settings = Column(JSON, default=dict, nullable=False)

    # Relationships
    members = relationship(
        "WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan"
    )
    projects = relationship(
        "Project", back_populates="workspace", cascade="all, delete-orphan"
    )
    documents = relationship(
        "Document", back_populates="workspace", cascade="all, delete-orphan"
    )
    meetings = relationship(
        "Meeting", back_populates="workspace", cascade="all, delete-orphan"
    )
    action_audits = relationship(
        "AgentActionAudit", back_populates="workspace", cascade="all, delete-orphan"
    )


class WorkspaceMember(Base, TimestampMixin):
    """Associates users with workspaces and defines their RBAC permissions."""
    __tablename__ = "workspace_members"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id = Column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role = Column(
        SQLEnum(WorkspaceRoleEnum, name="workspace_role_enum"),
        default=WorkspaceRoleEnum.MEMBER,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user_member"),
    )

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspace_memberships")


class WorkspaceInvitation(Base, TimestampMixin):
    """Pending email invitations for new team members to join a workspace."""
    __tablename__ = "workspace_invitations"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    email = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(WorkspaceRoleEnum, name="workspace_role_enum"),
        default=WorkspaceRoleEnum.MEMBER,
        nullable=False,
    )
    token = Column(String(255), unique=True, nullable=False)
    accepted = Column(String(32), default="pending", nullable=False)

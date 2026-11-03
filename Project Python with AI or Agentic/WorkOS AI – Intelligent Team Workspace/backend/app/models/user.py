from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class User(Base, TimestampMixin):
    """Registered user model for authentication and identity."""
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    mobile = Column(String(50), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    workspace_memberships = relationship(
        "WorkspaceMember", back_populates="user", cascade="all, delete-orphan"
    )
    assigned_tasks = relationship("Task", back_populates="assignee")
    comments = relationship("TaskComment", back_populates="author")

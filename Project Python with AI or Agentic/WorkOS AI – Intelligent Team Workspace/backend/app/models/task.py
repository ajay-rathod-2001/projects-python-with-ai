import enum
from sqlalchemy import (
    Column,
    String,
    Text,
    Date,
    Integer,
    ForeignKey,
    Enum as SQLEnum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid


class TaskStatusEnum(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriorityEnum(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, TimestampMixin):
    """Core task unit within a project, supporting Kanban drag-and-drop and dependencies."""
    __tablename__ = "tasks"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id = Column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TaskStatusEnum, name="task_status_enum"),
        default=TaskStatusEnum.TODO,
        index=True,
        nullable=False,
    )
    priority = Column(
        SQLEnum(TaskPriorityEnum, name="task_priority_enum"),
        default=TaskPriorityEnum.MEDIUM,
        nullable=False,
    )
    assignee_id = Column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    due_date = Column(Date, nullable=True)
    estimated_hours = Column(Integer, default=0, nullable=False)
    actual_hours = Column(Integer, default=0, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    
    dependencies = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    dependents = relationship(
        "TaskDependency",
        foreign_keys="TaskDependency.depends_on_task_id",
        back_populates="depends_on_task",
        cascade="all, delete-orphan",
    )

    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")


class TaskDependency(Base, TimestampMixin):
    """Direct acyclic graph edge representing dependency between tasks."""
    __tablename__ = "task_dependencies"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    task_id = Column(
        GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    depends_on_task_id = Column(
        GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    dependency_type = Column(String(50), default="blocks", nullable=False)

    __table_args__ = (
        UniqueConstraint("task_id", "depends_on_task_id", name="uq_task_dependency_pair"),
    )

    task = relationship("Task", foreign_keys=[task_id], back_populates="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], back_populates="dependents")


class TaskComment(Base, TimestampMixin):
    """Collaboration commentary on a specific task."""
    __tablename__ = "task_comments"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    task_id = Column(
        GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    author_id = Column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")


class TaskAttachment(Base, TimestampMixin):
    """Attached file or URL reference for a task."""
    __tablename__ = "task_attachments"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    task_id = Column(
        GUID(), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(1024), nullable=False)
    file_size_bytes = Column(Integer, nullable=True)

    task = relationship("Task", back_populates="attachments")

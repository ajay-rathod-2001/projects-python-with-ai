import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.base import TimestampMixin, GUID, generate_uuid

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None


class DocumentSourceEnum(str, enum.Enum):
    MANUAL = "manual"
    MEETING = "meeting"
    GITHUB = "github"
    UPLOAD = "upload"


class Document(Base, TimestampMixin):
    """Workspace knowledge document or meeting note used for RAG context."""
    __tablename__ = "documents"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    workspace_id = Column(
        GUID(), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id = Column(
        GUID(), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=True
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(
        SQLEnum(DocumentSourceEnum, name="document_source_enum"),
        default=DocumentSourceEnum.MANUAL,
        nullable=False,
    )
    metadata_json = Column(JSON, default=dict, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    project = relationship("Project", back_populates="documents")
    embeddings = relationship(
        "DocumentEmbedding", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentEmbedding(Base, TimestampMixin):
    """Vector chunk representation for semantic search and RAG."""
    __tablename__ = "document_embeddings"

    id = Column(GUID(), primary_key=True, default=generate_uuid)
    document_id = Column(
        GUID(), ForeignKey("documents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_content = Column(Text, nullable=False)

    # Vector embedding with standard JSON fallback
    if HAS_PGVECTOR:
        embedding_vector = Column(Vector(768), nullable=True)
    else:
        embedding_vector = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="embeddings")

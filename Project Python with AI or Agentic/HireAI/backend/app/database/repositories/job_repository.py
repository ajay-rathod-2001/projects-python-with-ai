"""Repository for JobDescription and JobRequirements CRUD operations."""

from sqlalchemy.orm import Session
from app.models.job import JobDescription, JobRequirements


class JobRepository:
    """Encapsulates database access for job descriptions and requirements."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> JobDescription:
        """Create and persist a new job description."""
        job = JobDescription(**kwargs)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: str) -> JobDescription | None:
        """Retrieve job by primary key."""
        return self.db.query(JobDescription).filter(JobDescription.id == job_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[JobDescription]:
        """List jobs with pagination."""
        return self.db.query(JobDescription).order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()

    def delete(self, job_id: str) -> bool:
        """Delete job description and cascading requirements."""
        job = self.get_by_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False

    def add_requirements(self, job_id: str, requirements: list[dict]) -> list[JobRequirements]:
        """Add batch of parsed job requirements."""
        req_objs = [
            JobRequirements(job_id=job_id, **req)
            for req in requirements
        ]
        self.db.add_all(req_objs)
        self.db.commit()
        return req_objs

"""Repository for Resume, ResumeInformation, and ResumeSkills CRUD operations."""

from sqlalchemy.orm import Session
from app.models.resume import Resume, ResumeInformation, ResumeSkills


class ResumeRepository:
    """Encapsulates database access for candidate resumes."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Resume:
        """Create and persist a new resume document record."""
        resume = Resume(**kwargs)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def get_by_id(self, resume_id: str) -> Resume | None:
        """Retrieve resume by primary key."""
        return self.db.query(Resume).filter(Resume.id == resume_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Resume]:
        """List resumes with pagination."""
        return self.db.query(Resume).order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, resume_id: str, **kwargs) -> Resume | None:
        """Update resume attributes."""
        resume = self.get_by_id(resume_id)
        if resume:
            for k, v in kwargs.items():
                setattr(resume, k, v)
            self.db.commit()
            self.db.refresh(resume)
        return resume

    def delete(self, resume_id: str) -> bool:
        """Delete resume record (cascading deletes information and skills)."""
        resume = self.get_by_id(resume_id)
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    def save_information(self, resume_id: str, **info_data) -> ResumeInformation:
        """Create or update structured personal and professional information."""
        info = self.db.query(ResumeInformation).filter(ResumeInformation.resume_id == resume_id).first()
        if info:
            for k, v in info_data.items():
                setattr(info, k, v)
        else:
            info = ResumeInformation(resume_id=resume_id, **info_data)
            self.db.add(info)
        self.db.commit()
        self.db.refresh(info)
        return info

    def add_skills(self, resume_id: str, skills_list: list[dict]) -> list[ResumeSkills]:
        """Add batch of extracted skills for a resume."""
        skill_objs = [
            ResumeSkills(resume_id=resume_id, **skill)
            for skill in skills_list
        ]
        self.db.add_all(skill_objs)
        self.db.commit()
        return skill_objs

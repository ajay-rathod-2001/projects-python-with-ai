"""Unit tests for SQLite database models, relations, cascades, and repositories."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.repositories import (
    ResumeRepository,
    JobRepository,
    MatchRepository,
    SettingsRepository,
)
from app.models import (
    Resume,
    ResumeInformation,
    ResumeSkills,
    JobDescription,
    JobRequirements,
    JobMatchAnalysis,
    SkillComparison,
    Recommendations,
    AnalysisHistory,
    ApplicationSettings,
)


@pytest.fixture
def db_session():
    """In-memory SQLite database session fixture with foreign key pragmas enabled."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Enable SQLite foreign key constraint enforcement
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON;")

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_resume_crud_and_cascades(db_session):
    """Verify Resume CRUD and automatic cascading deletion of information and skills."""
    repo = ResumeRepository(db_session)

    # 1. Create resume
    resume = repo.create(
        original_filename="test_resume.pdf",
        file_format="pdf",
        file_size_bytes=1024,
        stored_file_path="storage/resumes/test_uuid.pdf",
        raw_text="Sample candidate resume content",
    )
    assert resume.id is not None
    assert resume.processing_status == "pending"

    # 2. Attach resume information
    info = repo.save_information(
        resume_id=resume.id,
        full_name="Jane Doe",
        email="jane@example.com",
        location="Seattle, WA",
        education_json=[{"degree": "B.S. CS", "school": "UW"}],
    )
    assert info.id is not None
    assert info.resume_id == resume.id

    # 3. Add skills
    skills = repo.add_skills(
        resume_id=resume.id,
        skills_list=[
            {"skill_name": "Python", "category": "language", "evidence_text": "Built FastAPI APIs"},
            {"skill_name": "Docker", "category": "devops", "evidence_text": "Containerized apps"},
        ],
    )
    assert len(skills) == 2

    # Verify query
    fetched_resume = repo.get_by_id(resume.id)
    assert fetched_resume is not None
    assert fetched_resume.information.full_name == "Jane Doe"
    assert len(fetched_resume.skills) == 2

    # 4. Verify cascade deletion
    deleted = repo.delete(resume.id)
    assert deleted is True

    # Assert children were deleted
    assert repo.get_by_id(resume.id) is None
    assert db_session.query(ResumeInformation).filter(ResumeInformation.resume_id == resume.id).first() is None
    assert db_session.query(ResumeSkills).filter(ResumeSkills.resume_id == resume.id).count() == 0


def test_job_crud_and_requirements(db_session):
    """Verify JobDescription creation and requirements association."""
    repo = JobRepository(db_session)

    job = repo.create(
        title="Backend Engineer",
        company="Acme Corp",
        raw_text="Looking for a Python Backend Engineer",
        min_experience_years=3.0,
    )
    assert job.id is not None

    reqs = repo.add_requirements(
        job_id=job.id,
        requirements=[
            {
                "requirement_name": "Python",
                "category": "language",
                "classification": "mandatory",
                "evidence_text": "Must have Python experience",
            },
            {
                "requirement_name": "Kubernetes",
                "category": "devops",
                "classification": "preferred",
                "evidence_text": "Kubernetes is a plus",
            },
        ],
    )
    assert len(reqs) == 2

    fetched_job = repo.get_by_id(job.id)
    assert len(fetched_job.requirements) == 2

    # Delete cascade
    assert repo.delete(job.id) is True
    assert db_session.query(JobRequirements).filter(JobRequirements.job_id == job.id).count() == 0


def test_match_analysis_and_history(db_session):
    """Verify JobMatchAnalysis, SkillComparison, Recommendations, and History creation."""
    resume_repo = ResumeRepository(db_session)
    job_repo = JobRepository(db_session)
    match_repo = MatchRepository(db_session)

    # Setup parent entities
    resume = resume_repo.create(
        original_filename="alex.pdf",
        file_format="pdf",
        file_size_bytes=2048,
        stored_file_path="alex.pdf",
    )
    job = job_repo.create(
        title="Full Stack Engineer",
        company="Tech Inc",
        raw_text="Requires React and Python",
    )

    # Create atomic match analysis
    scores = {
        "overall_match_score": 85.0,
        "mandatory_skills_score": 35.0,
        "preferred_skills_score": 15.0,
        "experience_score": 15.0,
        "education_score": 10.0,
        "projects_score": 5.0,
        "responsibilities_score": 3.0,
        "soft_skills_score": 2.0,
    }
    weights = {"mandatory_skills": 40.0, "preferred_skills": 15.0}
    comparisons = [
        {
            "skill_name": "Python",
            "match_status": "matched",
            "semantic_score": 0.95,
            "resume_evidence": "Python developer",
            "explanation": "Exact skill matched",
        }
    ]
    recommendations = [
        {
            "type": "learning_path",
            "priority": "high",
            "target_skill": "TypeScript",
            "title": "Learn TypeScript",
            "description": "Master advanced TypeScript patterns",
            "rationale": "High priority requirement",
        }
    ]
    history_snapshot = {
        "resume_name": "alex.pdf",
        "job_title": "Full Stack Engineer",
        "company_name": "Tech Inc",
        "overall_score": 85.0,
        "matched_count": 1,
        "missing_count": 0,
    }

    analysis = match_repo.create_match_analysis(
        resume_id=resume.id,
        job_id=job.id,
        scores=scores,
        eligibility_status="satisfied",
        eligibility_summary="Candidate qualifies for this role",
        weights_applied=weights,
        comparisons=comparisons,
        recommendations=recommendations,
        history_snapshot=history_snapshot,
    )

    assert analysis.id is not None
    assert analysis.overall_match_score == 85.0
    assert len(analysis.comparisons) == 1
    assert len(analysis.recommendations) == 1
    assert analysis.history_entry is not None

    # Verify history listing
    history_list = match_repo.list_history()
    assert len(history_list) == 1
    assert history_list[0].job_title == "Full Stack Engineer"


def test_settings_repository(db_session):
    """Verify key-value JSON settings persistence."""
    repo = SettingsRepository(db_session)

    # Set setting
    default_weights = {"mandatory": 40.0, "preferred": 15.0}
    repo.set("scoring_weights", default_weights)

    # Retrieve setting
    val = repo.get("scoring_weights")
    assert val == default_weights

    # Update setting
    updated_weights = {"mandatory": 50.0, "preferred": 10.0}
    repo.set("scoring_weights", updated_weights)
    val2 = repo.get("scoring_weights")
    assert val2["mandatory"] == 50.0

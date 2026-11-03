"""SQLAlchemy ORM Database Models Package.

Exports all core and extended domain models for HireAI.
"""

from app.models.resume import Resume, ResumeInformation, ResumeSkills
from app.models.job import JobDescription, JobRequirements
from app.models.match import JobMatchAnalysis, SkillComparison
from app.models.recommendation import Recommendations
from app.models.history import AnalysisHistory
from app.models.settings import ApplicationSettings
from app.models.assessment import AssessmentQuestion, AssessmentSubmission
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.auth import User

__all__ = [
    "Resume",
    "ResumeInformation",
    "ResumeSkills",
    "JobDescription",
    "JobRequirements",
    "JobMatchAnalysis",
    "SkillComparison",
    "Recommendations",
    "AnalysisHistory",
    "ApplicationSettings",
    "AssessmentQuestion",
    "AssessmentSubmission",
    "InterviewSession",
    "InterviewQuestion",
    "User",
]

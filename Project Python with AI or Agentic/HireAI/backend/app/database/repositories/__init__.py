"""Database Repositories Package.

Exports repository abstractions for Resume, Job, Matching, and Settings.
"""

from app.database.repositories.resume_repository import ResumeRepository
from app.database.repositories.job_repository import JobRepository
from app.database.repositories.match_repository import MatchRepository
from app.database.repositories.settings_repository import SettingsRepository

__all__ = [
    "ResumeRepository",
    "JobRepository",
    "MatchRepository",
    "SettingsRepository",
]

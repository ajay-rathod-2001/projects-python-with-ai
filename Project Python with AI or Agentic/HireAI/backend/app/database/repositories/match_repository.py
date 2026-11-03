"""Repository for JobMatchAnalysis, SkillComparison, Recommendations, and History."""

from sqlalchemy.orm import Session
from app.models.match import JobMatchAnalysis, SkillComparison
from app.models.recommendation import Recommendations
from app.models.history import AnalysisHistory


class MatchRepository:
    """Encapsulates database access for matching, scoring, recommendations, and history."""

    def __init__(self, db: Session):
        self.db = db

    def create_match_analysis(
        self,
        resume_id: str,
        job_id: str,
        scores: dict,
        eligibility_status: str,
        eligibility_summary: str,
        weights_applied: dict,
        comparisons: list[dict],
        recommendations: list[dict],
        history_snapshot: dict,
    ) -> JobMatchAnalysis:
        """Create a complete match analysis with comparisons, recommendations, and audit history atomically."""
        analysis = JobMatchAnalysis(
            resume_id=resume_id,
            job_id=job_id,
            overall_match_score=scores.get("overall_match_score", 0.0),
            mandatory_skills_score=scores.get("mandatory_skills_score", 0.0),
            preferred_skills_score=scores.get("preferred_skills_score", 0.0),
            experience_score=scores.get("experience_score", 0.0),
            education_score=scores.get("education_score", 0.0),
            projects_score=scores.get("projects_score", 0.0),
            responsibilities_score=scores.get("responsibilities_score", 0.0),
            soft_skills_score=scores.get("soft_skills_score", 0.0),
            eligibility_status=eligibility_status,
            eligibility_summary=eligibility_summary,
            weights_applied_json=weights_applied,
        )
        self.db.add(analysis)
        self.db.flush()  # Populates analysis.id

        # Insert skill comparisons
        for comp in comparisons:
            self.db.add(SkillComparison(match_analysis_id=analysis.id, **comp))

        # Insert recommendations
        for rec in recommendations:
            self.db.add(Recommendations(match_analysis_id=analysis.id, **rec))

        # Insert analysis history snapshot
        self.db.add(AnalysisHistory(match_analysis_id=analysis.id, **history_snapshot))

        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_analysis_by_id(self, analysis_id: str) -> JobMatchAnalysis | None:
        """Retrieve match analysis with relationships."""
        return self.db.query(JobMatchAnalysis).filter(JobMatchAnalysis.id == analysis_id).first()

    def list_history(self, limit: int = 50) -> list[AnalysisHistory]:
        """List historical analyses for dashboard overview."""
        return self.db.query(AnalysisHistory).order_by(AnalysisHistory.analysis_date.desc()).limit(limit).all()

    def delete_history_entry(self, history_id: str) -> bool:
        """Delete historical entry and associated match analysis."""
        entry = self.db.query(AnalysisHistory).filter(AnalysisHistory.id == history_id).first()
        if entry:
            analysis = entry.match_analysis
            if analysis:
                self.db.delete(analysis)
            else:
                self.db.delete(entry)
            self.db.commit()
            return True
        return False

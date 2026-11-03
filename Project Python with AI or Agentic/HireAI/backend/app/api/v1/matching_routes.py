"""Matching API endpoints (Resume vs Job Comparison, 100-Point Scoring, and Persistence)."""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai_engine.job_analyzer import JobAnalyzer
from app.ai_engine.matching_engine import MatchingEngine
from app.ai_engine.recommendation_engine import RecommendationEngine
from app.ai_engine.scoring_engine import ScoringEngine
from app.ai_engine.skill_extractor import SkillExtractor
from app.database.connection import get_db
from app.models.history import AnalysisHistory
from app.models.job import JobDescription, JobRequirements
from app.models.match import JobMatchAnalysis, SkillComparison
from app.models.recommendation import Recommendations
from app.models.resume import Resume, ResumeInformation, ResumeSkills

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matching", tags=["Matching"])

matching_engine = MatchingEngine()
scoring_engine = ScoringEngine()
recommendation_engine = RecommendationEngine()
skill_extractor = SkillExtractor()
job_analyzer = JobAnalyzer()


class MatchAnalyzeRequest(BaseModel):
    """Payload to trigger match analysis between resume and job."""
    resume_id: str | None = None
    job_id: str | None = None
    resume_text: str | None = None
    job_text: str | None = None


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_match(payload: MatchAnalyzeRequest, db: Session = Depends(get_db)):
    """Perform compatibility scoring and skill comparison between a candidate resume and job posting."""
    resume = None
    job = None

    # 1. Resolve Resume
    if payload.resume_id:
        resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail=f"Resume '{payload.resume_id}' not found.")
    elif payload.resume_text:
        # Create on the fly
        resume_id = str(uuid.uuid4())
        raw_r_text = payload.resume_text.strip()
        info_dict = skill_extractor.extract_candidate_info(raw_r_text)
        skills_list = skill_extractor.extract_skills(raw_r_text)

        cand_name = info_dict.get("full_name") or "Direct Input Candidate"
        resume = Resume(
            id=resume_id,
            original_filename="candidate_resume.txt",
            file_format="txt",
            file_size_bytes=len(raw_r_text.encode("utf-8")),
            stored_file_path="",
            raw_text=raw_r_text,
            processing_status="completed",
        )
        db.add(resume)

        info_rec = ResumeInformation(
            resume_id=resume_id,
            full_name=cand_name,
            email=info_dict.get("email"),
            phone=info_dict.get("phone"),
            location=info_dict.get("location"),
            summary=info_dict.get("summary"),
            education_json=info_dict.get("education"),
            experience_json=info_dict.get("experience"),
            projects_json=info_dict.get("projects"),
        )
        db.add(info_rec)

        for s in skills_list:
            db.add(ResumeSkills(
                resume_id=resume_id,
                skill_name=s["skill_name"],
                category=s["category"],
                years_of_experience=s.get("years_of_experience"),
                evidence_text=s.get("evidence_text"),
            ))
        db.commit()
        db.refresh(resume)
    else:
        # Fallback to most recent uploaded resume if available
        resume = db.query(Resume).order_by(Resume.created_at.desc()).first()
        if not resume:
            raise HTTPException(status_code=400, detail="Please upload or select a resume first.")

    # 2. Resolve Job
    if payload.job_id:
        job = db.query(JobDescription).filter(JobDescription.id == payload.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job '{payload.job_id}' not found.")
    elif payload.job_text:
        # Create on the fly
        job_id = str(uuid.uuid4())
        raw_j_text = payload.job_text.strip()
        j_analysis = job_analyzer.analyze_job(raw_j_text)

        job = JobDescription(
            id=job_id,
            title=j_analysis.get("title") or "Software Engineer",
            company=j_analysis.get("company") or "Target Company",
            location=j_analysis.get("location") or "Remote",
            raw_text=raw_j_text,
            source_type="paste",
            min_experience_years=j_analysis.get("min_experience_years", 2.0),
            education_level=j_analysis.get("education_level", "Bachelor's Degree"),
        )
        db.add(job)

        for r in j_analysis.get("requirements", []):
            db.add(JobRequirements(
                job_id=job_id,
                requirement_name=r["requirement_name"],
                category=r["category"],
                classification=r["classification"],
                required_experience_years=r.get("required_experience_years"),
                evidence_text=r["evidence_text"],
            ))
        db.commit()
        db.refresh(job)
    else:
        # Fallback to most recent parsed job if available
        job = db.query(JobDescription).order_by(JobDescription.created_at.desc()).first()
        if not job:
            raise HTTPException(status_code=400, detail="Please paste or select a job description.")

    # 3. Prepare Structures for Matching
    resume_skills_data = [
        {
            "id": s.id,
            "skill_name": s.skill_name,
            "category": s.category,
            "years_of_experience": s.years_of_experience,
            "evidence_text": s.evidence_text,
        }
        for s in resume.skills
    ]

    job_reqs_data = [
        {
            "id": r.id,
            "requirement_name": r.requirement_name,
            "category": r.category,
            "classification": r.classification,
            "required_experience_years": r.required_experience_years,
            "evidence_text": r.evidence_text,
        }
        for r in job.requirements
    ]

    candidate_info_dict = {
        "full_name": resume.information.full_name if resume.information else "Candidate",
        "education": resume.information.education_json if resume.information else [],
        "experience": resume.information.experience_json if resume.information else [],
        "projects": resume.information.projects_json if resume.information else [],
    }

    job_info_dict = {
        "title": job.title,
        "company": job.company,
        "min_experience_years": job.min_experience_years,
    }

    # 4. Execute Semantic Matching
    comparisons = matching_engine.compare_skills(
        resume_skills=resume_skills_data,
        job_requirements=job_reqs_data,
        resume_raw_text=resume.raw_text or "",
    )

    # 5. Compute Deterministic 100-Point Score
    score_result = scoring_engine.calculate_score(
        comparisons=comparisons,
        candidate_info=candidate_info_dict,
        job_info=job_info_dict,
    )

    # 6. Generate Actionable Career Recommendations
    recommendations_result = recommendation_engine.generate_recommendations(
        comparisons=comparisons,
        candidate_info=candidate_info_dict,
        job_info=job_info_dict,
    )

    # 7. Persist Analysis into Database
    analysis_id = str(uuid.uuid4())
    match_analysis = JobMatchAnalysis(
        id=analysis_id,
        resume_id=resume.id,
        job_id=job.id,
        overall_match_score=score_result["overall_match_score"],
        mandatory_skills_score=score_result["category_scores"]["mandatory_skills"],
        preferred_skills_score=score_result["category_scores"]["preferred_skills"],
        experience_score=score_result["category_scores"]["experience_alignment"],
        education_score=score_result["category_scores"]["education_alignment"],
        projects_score=score_result["category_scores"]["projects_practical"],
        responsibilities_score=score_result["category_scores"]["responsibilities"],
        soft_skills_score=score_result["category_scores"]["soft_skills"],
        eligibility_status=score_result["eligibility_status"],
        eligibility_summary=score_result["eligibility_summary"],
        weights_applied_json=score_result["weights_applied"],
    )
    db.add(match_analysis)

    # Persist Individual Skill Comparisons
    for c in comparisons:
        comp_rec = SkillComparison(
            match_analysis_id=analysis_id,
            requirement_id=c.get("requirement_id"),
            skill_name=c["skill_name"],
            match_status=c["match_status"],
            semantic_score=c["semantic_score"],
            resume_evidence=c.get("resume_evidence"),
            explanation=c["explanation"],
        )
        db.add(comp_rec)

    # Persist Recommendations
    for lr in recommendations_result.get("learning_roadmap", []):
        db.add(Recommendations(
            match_analysis_id=analysis_id,
            type="learning_path",
            priority=lr.get("priority", "medium"),
            target_skill=lr.get("target_skill"),
            title=lr.get("title", ""),
            description=lr.get("description", ""),
            rationale=lr.get("rationale", ""),
        ))

    # Persist Analysis History Record
    matched_count = sum(1 for c in comparisons if c["match_status"] == "matched")
    missing_count = sum(1 for c in comparisons if c["match_status"] in ("missing", "partially_matched"))
    cand_name = resume.information.full_name if resume.information else "Candidate"

    db.add(AnalysisHistory(
        match_analysis_id=analysis_id,
        resume_name=cand_name,
        job_title=job.title,
        company_name=job.company,
        overall_score=score_result["overall_match_score"],
        matched_count=matched_count,
        missing_count=missing_count,
    ))

    db.commit()

    return {
        "match_analysis_id": analysis_id,
        "resume_id": resume.id,
        "job_id": job.id,
        "candidate_name": cand_name,
        "job_title": job.title,
        "company": job.company,
        "overall_match_score": score_result["overall_match_score"],
        "category_scores": score_result["category_scores"],
        "eligibility": {
            "status": score_result["eligibility_status"],
            "summary": score_result["eligibility_summary"],
        },
        "skill_comparisons": comparisons,
        "recommendations": recommendations_result,
        "created_at": match_analysis.created_at.isoformat(),
    }


@router.get("/{analysis_id}")
async def get_match_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Retrieve full compatibility score, skill comparisons, and recommendations for an analysis."""
    analysis = db.query(JobMatchAnalysis).filter(JobMatchAnalysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Match analysis '{analysis_id}' not found.")

    comparisons = [
        {
            "id": c.id,
            "skill_name": c.skill_name,
            "match_status": c.match_status,
            "semantic_score": c.semantic_score,
            "resume_evidence": c.resume_evidence,
            "explanation": c.explanation,
        }
        for c in analysis.comparisons
    ]

    recommendations = [
        {
            "id": r.id,
            "type": r.type,
            "priority": r.priority,
            "target_skill": r.target_skill,
            "title": r.title,
            "description": r.description,
            "rationale": r.rationale,
        }
        for r in analysis.recommendations
    ]

    return {
        "match_analysis_id": analysis.id,
        "resume_id": analysis.resume_id,
        "job_id": analysis.job_id,
        "overall_match_score": analysis.overall_match_score,
        "category_scores": {
            "mandatory_skills": analysis.mandatory_skills_score,
            "preferred_skills": analysis.preferred_skills_score,
            "experience_alignment": analysis.experience_score,
            "education_alignment": analysis.education_score,
            "projects_practical": analysis.projects_score,
            "responsibilities": analysis.responsibilities_score,
            "soft_skills": analysis.soft_skills_score,
        },
        "eligibility": {
            "status": analysis.eligibility_status,
            "summary": analysis.eligibility_summary,
        },
        "skill_comparisons": comparisons,
        "recommendations": recommendations,
        "created_at": analysis.created_at.isoformat(),
    }

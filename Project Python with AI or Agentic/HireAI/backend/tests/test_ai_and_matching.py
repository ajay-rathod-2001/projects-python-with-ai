"""Integration tests for AI extraction, document parsing, matching, and scoring."""

from app.ai_engine.job_analyzer import JobAnalyzer
from app.ai_engine.matching_engine import MatchingEngine
from app.ai_engine.recommendation_engine import RecommendationEngine
from app.ai_engine.scoring_engine import ScoringEngine
from app.ai_engine.skill_extractor import SkillExtractor


def test_skill_extractor_standard_skills():
    """Verify standard skills and contextual evidence are extracted properly."""
    extractor = SkillExtractor()
    sample_text = (
        "Sarah Jenkins\nsarah@example.com\n"
        "Senior Software Engineer with 5+ years of experience in Python and FastAPI. "
        "Built scalable microservices deployed with Docker and Kubernetes on AWS. "
        "Proficient in PostgreSQL and Redis caching."
    )
    skills = extractor.extract_skills(sample_text)
    names = {s["skill_name"] for s in skills}

    assert "Python" in names
    assert "FastAPI" in names
    assert "Docker" in names
    assert "Kubernetes" in names
    assert "AWS" in names
    assert "PostgreSQL" in names
    assert "Redis" in names


def test_candidate_info_extraction():
    """Verify name, email, and education extraction."""
    extractor = SkillExtractor()
    sample_text = (
        "Alex Morgan\n"
        "alex.morgan@email.com\n"
        "Seattle, WA\n\n"
        "Bachelor of Science in Computer Science, University of Washington, 2020\n"
        "Senior Software Engineer with extensive experience in Go and Python."
    )
    info = extractor.extract_candidate_info(sample_text)
    assert info["email"] == "alex.morgan@email.com"
    assert info["full_name"] == "Alex Morgan"
    assert len(info["education"]) > 0


def test_job_analyzer_classification():
    """Verify job analyzer classifies mandatory and preferred skills."""
    analyzer = JobAnalyzer()
    job_text = (
        "Senior Software Engineer\n"
        "Required Qualifications:\n"
        "• Minimum 5+ years of production experience in Python and FastAPI.\n"
        "• Proven experience with PostgreSQL database optimization.\n"
        "Preferred Qualifications:\n"
        "• Hands-on experience with Docker and Kubernetes.\n"
        "• Familiarity with Redis caching."
    )
    result = analyzer.analyze_job(job_text)
    reqs = result["requirements"]
    assert len(reqs) > 0

    req_names = {r["requirement_name"]: r["classification"] for r in reqs}
    assert "Python" in req_names


def test_matching_and_100_point_scoring():
    """Verify matching engine evaluates skills and scoring engine outputs 100-point score."""
    matcher = MatchingEngine()
    scorer = ScoringEngine()

    resume_skills = [
        {"skill_name": "Python", "category": "language", "evidence_text": "Built Python APIs."},
        {"skill_name": "FastAPI", "category": "framework", "evidence_text": "Used FastAPI."},
        {"skill_name": "Docker", "category": "devops", "evidence_text": "Dockerized apps."},
    ]

    job_reqs = [
        {"requirement_name": "Python", "classification": "mandatory", "category": "language"},
        {"requirement_name": "FastAPI", "classification": "mandatory", "category": "framework"},
        {"requirement_name": "Kubernetes", "classification": "preferred", "category": "devops"},
    ]

    candidate_info = {"experience": [{"title": "Senior Engineer"}], "education": [{"degree": "BS CS"}]}
    job_info = {"title": "Software Engineer", "company": "Test Co", "min_experience_years": 3.0}

    comparisons = matcher.compare_skills(resume_skills, job_reqs, resume_raw_text="Built Python APIs with FastAPI.")
    assert len(comparisons) == 3

    score_result = scorer.calculate_score(comparisons, candidate_info, job_info)
    assert 0.0 <= score_result["overall_match_score"] <= 100.0
    assert "mandatory_skills" in score_result["category_scores"]
    assert score_result["eligibility_status"] in ("satisfied", "partially_satisfied", "not_satisfied")


def test_recommendation_engine():
    """Verify recommendation engine produces actionable roadmaps and interview questions."""
    recommender = RecommendationEngine()
    comparisons = [
        {"skill_name": "Python", "match_status": "matched", "requirement_category": "mandatory"},
        {"skill_name": "Kubernetes", "match_status": "missing", "requirement_category": "preferred"},
    ]
    candidate_info = {"experience": [{"title": "Backend Engineer"}]}
    job_info = {"title": "Staff Engineer"}

    recs = recommender.generate_recommendations(comparisons, candidate_info, job_info)
    assert len(recs["learning_roadmap"]) > 0
    assert len(recs["project_suggestions"]) > 0
    assert len(recs["resume_improvements"]) > 0
    assert len(recs["interview_prep"]) > 0


def test_full_api_workflow(client):
    """Verify full upload -> job -> matching API flow."""
    # 1. Manual resume upload
    resume_resp = client.post(
        "/api/v1/resumes/manual",
        json={
            "raw_text": (
                "John Developer\njohn@example.com\n"
                "Experienced Software Engineer in Python, FastAPI, and Docker."
            ),
            "candidate_name": "John Developer",
        },
    )
    assert resume_resp.status_code == 201
    resume_id = resume_resp.json()["id"]

    # 2. Post Job
    job_resp = client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Developer",
            "company": "Tech Innovators",
            "raw_text": "We are seeking a Python Developer with strong FastAPI and Docker experience.",
        },
    )
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    # 3. Analyze Compatibility
    match_resp = client.post(
        "/api/v1/matching/analyze",
        json={"resume_id": resume_id, "job_id": job_id},
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()
    assert match_data["overall_match_score"] > 50
    assert len(match_data["skill_comparisons"]) > 0
    assert "recommendations" in match_data


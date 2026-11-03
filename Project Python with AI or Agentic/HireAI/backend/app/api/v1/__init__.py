"""API Version 1 Package for HireAI."""

from fastapi import APIRouter
from app.api.v1.resume_routes import router as resume_router
from app.api.v1.job_routes import router as job_router
from app.api.v1.matching_routes import router as matching_router
from app.api.v1.recommendation_routes import router as recommendation_router
from app.api.v1.report_routes import router as report_router
from app.api.v1.assessment_routes import router as assessment_router
from app.api.v1.interview_routes import router as interview_router
from app.api.v1.auth_routes import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")


@api_v1_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for HireAI API services."""
    return {
        "status": "success",
        "application": "HireAI – Intelligent Recruitment & Technical Assessment Platform",
        "version": "1.0.0",
        "services": {
            "resume_parser": "online",
            "jd_analyzer": "online",
            "matching_engine": "online",
            "assessment_workers": "online",
            "interview_copilot": "online",
        },
    }


# Include all domain routers
api_v1_router.include_router(resume_router)
api_v1_router.include_router(job_router)
api_v1_router.include_router(matching_router)
api_v1_router.include_router(recommendation_router)
api_v1_router.include_router(report_router)
api_v1_router.include_router(assessment_router)
api_v1_router.include_router(interview_router)
api_v1_router.include_router(auth_router)

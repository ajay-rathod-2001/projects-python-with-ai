from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "workos_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Periodic Risk Analysis Scheduler
    beat_schedule={
        "scan-project-risks-every-15-min": {
            "task": "app.workers.tasks.run_scheduled_project_risk_scan",
            "schedule": 900.0,  # 15 minutes
        },
    },
)


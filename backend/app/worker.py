from celery import Celery
from app.config import settings

celery_app = Celery(
    "acadeval",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Phase 2: import AI task modules here
# celery_app.autodiscover_tasks(["app.tasks"])

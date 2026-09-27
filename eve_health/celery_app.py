import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# If testing, we use memory broker to avoid needing redis locally
if os.environ.get("TESTING", "False").lower() == "true":
    celery_app = Celery("eve_health", broker="memory://", backend="cache+memory://")
    celery_app.conf.task_always_eager = True
else:
    celery_app = Celery("eve_health", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    include=["eve_health.tasks"],
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

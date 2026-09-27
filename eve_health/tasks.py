import httpx
import time
from .celery_app import celery_app
from loguru import logger

@celery_app.task(bind=True, max_retries=3)
def trigger_webhook_task(self, url: str, payload: dict):
    # Simulate a delay in webhook delivery
    time.sleep(2)
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
    except Exception as exc:
        logger.error(f"Failed to trigger webhook, retrying: {exc}")
        raise self.retry(exc=exc, countdown=5)

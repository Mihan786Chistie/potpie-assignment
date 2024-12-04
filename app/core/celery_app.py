import logging
from celery import Celery
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery_app = Celery(
    "worker",
    backend=settings.CELERY_RESULT_BACKEND,
    broker=settings.CELERY_BROKER_URL
)

celery_app.conf.task_routes = {
    "app.services.ai_agent.analyze_pr": "main-queue"
}

@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Celery app configured")

@celery_app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')


from celery import Celery
from app.core.config import settings

celery_app = Celery("app", backend=settings.CELERY_BACKEND_URL,
                    include=['app.core.tasks']
                    )
celery_app.config_from_object(settings, namespace='CELERY')

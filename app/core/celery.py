from celery import Celery
from app.core.config import settings


celery = Celery(__name__ , include=["app.core.tasks"])



celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND




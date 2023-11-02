from celery import Celery
import sentry_sdk
from app.core.config import settings

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    enable_tracing=True,
)


celery = Celery(
    __name__,
    include=['app.core.instagram.tasks', 'app.core.telegram.tasks',
             'app.core.notifier.tasks', 'app.core.tasks'],
)

celery.conf.broker_url = str(settings.CELERY_URI)
celery.conf.result_backend = str(settings.CELERY_URI)
celery.conf.broker_connection_retry_on_startup = True
celery.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
)

celery.conf.beat_schedule = {
    'campaign-terminal-every-1-hour': {
        'task': 'app.core.notifier.tasks.campaign_terminal',
        'schedule': 3600,
    },
}

from celery import Celery
from app.core.config import settings

# from app.core.notifier.tasks import campaign_terminal

celery = Celery(
    __name__, include=["app.core.bot_builder.tasks", "app.core.notifier.tasks" , "app.core.tasks"]
)

celery.conf.broker_url = settings.CELERY_URI
celery.conf.result_backend = settings.CELERY_URI
celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery.conf.beat_schedule = {
    'campaign-terminal-every-1-hour': {
        'task': 'app.core.notifier.tasks.campaign_terminal',
        'schedule': 3600,
    },
}

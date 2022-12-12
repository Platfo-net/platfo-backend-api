from celery import Celery
from app.core.config import settings

# from app.core.postman.tasks import campaign_terminal

celery = Celery(
    __name__, include=["app.core.bot_builder.tasks", "app.core.postman.tasks"]
)

celery.conf.broker_url = settings.CELERY_URI
celery.conf.result_backend = settings.CELERY_URI


# @celery.on_after_configure.connect
# def schedule_task(sender, **kwargs):
#     sender.add_periodic_task(
#         settings.CAMPAIGN_PERIOD_INTERVAL_MINUTES * 60,
#         campaign_terminal.s(), expires=10
#         )

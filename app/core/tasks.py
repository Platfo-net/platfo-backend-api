from celery import shared_task

from app.core.config import settings
from app.core import sms


@shared_task
def send_user_activation_code(receptor, code):
    sms.send_verify_sms(receptor, code, settings.KAVE_NEGAR_USER_ACTIVATE_TEMPLATE)


@shared_task
def send_user_reset_password_code(receptor, code):
    sms.send_verify_sms(receptor, code, settings.KAVE_NEGAR_RESET_PASSWORD_TEMPLATE)

from app.core.celery import celery

from app.core.config import settings
from app.core import sms


@celery.task
def send_user_activation_code(receptor, code):
    return sms.send_verify_sms(receptor, code, settings.SMS_IR_USER_ACTIVATION_TEMPLATE_ID)


@celery.task
def send_user_reset_password_code(receptor, code):
    sms.send_verify_sms(receptor, code, settings.SMS_IR_USER_RESET_PASSWORD_TEMPLATE_ID)

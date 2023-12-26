from app import models, services
from app.core.unit_of_work import UnitOfWork
from app.db.session import SessionLocal
from app.core.celery import celery
from app.core.config import settings
from app.core.sms import send_verify_sms


@celery.task
def send_user_activation_code(receptor, code):
    return send_verify_sms(receptor, code, settings.SMS_IR_USER_ACTIVATION_TEMPLATE_ID)


@celery.task
def send_user_reset_password_code(receptor, code):
    return send_verify_sms(
        receptor, code, settings.SMS_IR_USER_RESET_PASSWORD_TEMPLATE_ID
    )


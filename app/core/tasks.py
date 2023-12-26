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


@celery.task
def add_all_payment_for_shop():
    db = SessionLocal()

    payment_methods = services.shop.payment_method.all(db)
    shops = db.query(models.shop.ShopShop).all()
    for payment_method in payment_methods:
        for shop in shops:
            shop_payment_method = services.shop.shop_payment_method.get_by_payment_method_and_shop_id(
                db, shop_id=shop.id, payment_method_id=payment_method.id)
            if not shop_payment_method:
                with UnitOfWork(db) as uow:
                    services.shop.shop_payment_method.create(
                        uow, shop_id=shop.id, payment_method_id=payment_method.id)

import asyncio
from typing import Optional

from app import services
from app.core.celery import celery
from app.core.telegram import (admin_bot_handlers, bot_handlers, handlers,
                               support_bot_handlers)
from app.db.session import SessionLocal


@celery.task
def send_create_shop_notification_to_all_admins_task(shop_id, lang: str):
    db = SessionLocal()
    asyncio.run(
        admin_bot_handlers.send_create_shop_notification_to_all_admins_handler(
            db, shop_id, lang)
    )
    db.close()


@celery.task
def send_register_user_notification_to_all_admins_task(user_id, lang: str):
    db = SessionLocal()
    asyncio.run(
        admin_bot_handlers.send_register_user_notification_to_all_admins_handler(
            db, user_id, lang)
    )
    db.close()


@celery.task
def telegram_message_builder_bot_task(data, lang: str):
    db = SessionLocal()
    asyncio.run(handlers.telegram_message_builder_bot_handler(db, data, lang))

    db.close()

@celery.task
def telegram_admin_bot_task(data, lang: str):
    db = SessionLocal()
    asyncio.run(handlers.telegram_admin_bot_handler(db, data, lang))

    db.close()


@celery.task
def telegram_support_bot_task(data, lang: str):
    db = SessionLocal()
    asyncio.run(handlers.telegram_support_bot_handler(db, data, lang))

    db.close()


@celery.task
def telegram_webhook_task(data: dict, bot_id: int, lang):
    db = SessionLocal()
    asyncio.run(handlers.telegram_bot_webhook_handler(db, data, bot_id, lang))

    db.close()


@celery.task
def send_lead_order_to_bot_and_support_bot_task(
        telegram_bot_id: int, lead_id: int, order_id: Optional[int], telegram_order_id: int, lang):
    db = SessionLocal()
    bot_message_id = None
    if lead_id:
        bot_message_id = asyncio.run(bot_handlers.send_lead_order_to_bot_handler(
            db, telegram_bot_id, lead_id, order_id, lang))

    support_bot_message_id = asyncio.run(
        support_bot_handlers.send_lead_order_to_shop_support_bot(
            db, telegram_bot_id, lead_id, order_id, lang,
        )
    )
    services.shop.telegram_order.add_message_info(
        db,
        telegram_order_id=telegram_order_id,
        bot_message_id=bot_message_id,
        support_bot_message_id=support_bot_message_id,
    )

    db.close()


@celery.task
def send_lead_pay_notification_to_support_bot_task(order_id: int, lang: str):
    db = SessionLocal()
    asyncio.run(support_bot_handlers.send_lead_pay_notification_to_support_bot_handler(
        db, order_id, lang))

    db.close()


@celery.task
def send_shop_bot_connection_notification_task(shop_telegram_bot_id: int, lang):
    db = SessionLocal()
    asyncio.run(
        support_bot_handlers.send_shop_bot_connection_notification_handler(
            db,
            shop_telegram_bot_id,
            lang,
        )
    )

    db.close()


@celery.task
def send_expiration_soon_notification_task():
    db = SessionLocal()
    asyncio.run(
        support_bot_handlers.send_expiration_soon_notification(
            db,
            "fa",
        )
    )
    db.close()


@celery.task
def set_all_bot_commands_task():
    db = SessionLocal()
    asyncio.run(
        bot_handlers.set_all_bot_commands_task_handler(
            db, "fa"
        )
    )
    db.close()


@celery.task
def send_credit_extending_successful_notification_task(
        shop_credit_id, shop_telegram_payment_record_id):
    db = SessionLocal()

    asyncio.run(support_bot_handlers.send_credit_extending_successful_notification_handler(
        db, shop_credit_id, shop_telegram_payment_record_id, "fa"
    ))

    db.close()


@celery.task
def send_lead_pay_notification_to_bot_task(
    order_id: int, lang: str
):
    db = SessionLocal()

    asyncio.run(bot_handlers.send_lead_pay_notification_to_bot_handler(
        db, order_id, lang
    )
    )
    db.close()


@celery.task
def order_change_status_from_dashboard_task(order_id, lang):
    db = SessionLocal()
    asyncio.run(
        bot_handlers.order_change_status_from_dashboard_handler(db, order_id, lang)
    )
    db.close()


@celery.task
def send_shop_order_report_task(lang, shop_id, amount, currency, count, date):
    db = SessionLocal()
    asyncio.run(
        support_bot_handlers.send_shop_order_report(
            db, lang, shop_id, amount, currency, count, date)
    )
    db.close()

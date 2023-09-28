import asyncio
from app.core.celery import celery
from app.core.telegram import support_bot_handlers, bot_handlers, handlers
from app.db.session import SessionLocal


@celery.task
def telegram_support_bot_task(data, lang: str):
    db = SessionLocal()
    asyncio.run(handlers.telegram_support_bot_handler(db, data, lang))

    db.close()


@celery.task
def telegram_webhook_task(data: dict, bot_id: int):
    db = SessionLocal()
    asyncio.run(handlers.telegram_bot_webhook_handler(db, data, bot_id=bot_id))

    db.close()


@celery.task
def send_lead_order_to_bot_task(telegram_bot_id: int, lead_id: int, order_id: int):
    db = SessionLocal()
    asyncio.run(bot_handlers.send_lead_order_to_bot_handler(
        db, telegram_bot_id, lead_id, order_id))

    db.close()


@celery.task
def send_lead_pay_notification_to_support_bot_task(order_id: int, lang: str):
    db = SessionLocal()
    asyncio.run(support_bot_handlers.send_lead_pay_notification_to_support_bot_handler(
        db, order_id, lang))

    db.close()


@celery.task
def send_lead_order_to_shop_support_task(telegram_bot_id: int, lead_id: int, order_id: int, lang):
    db = SessionLocal()
    asyncio.run(
        support_bot_handlers.send_lead_order_to_shop_support_handler(
            db,
            telegram_bot_id,
            lead_id,
            order_id,
            lang,
        )
    )

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

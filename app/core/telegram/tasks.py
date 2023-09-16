import asyncio

from app.core.celery import celery
from app.core.telegram import handlers as telegram_handlers
from app.db.session import SessionLocal


@celery.task
def telegram_support_bot_task(data, lang: str):
    db = SessionLocal()
    asyncio.run(telegram_handlers.telegram_support_bot_handler(db, data, lang))

    db.close()


@celery.task
def telegram_webhook_task(data: dict, bot_id: int):
    db = SessionLocal()
    try:
        asyncio.run(telegram_handlers.telegram_bot_webhook_handler(db, data, bot_id=bot_id))
    except Exception as e:
        print(e)

    db.close()


@celery.task
def send_lead_order_to_bot_task(telegram_bot_id: int, lead_id: int, order_id: int):
    db = SessionLocal()
    try:
        asyncio.run(telegram_handlers.send_lead_order_to_bot_handler(
            db, telegram_bot_id, lead_id, order_id))
    except Exception as e:
        print(e)

    db.close()


@celery.task
def send_lead_order_to_shop_support_task(telegram_bot_id: int, lead_id: int, order_id: int, lang):
    db = SessionLocal()
    try:
        asyncio.run(
            telegram_handlers.send_lead_order_to_shop_support_handler(
                db,
                telegram_bot_id,
                lead_id, order_id,
                lang,
            )
        )
    except Exception as e:
        print(e)

    db.close()

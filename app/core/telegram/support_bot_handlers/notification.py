
from datetime import datetime

from sqlalchemy.orm import Session
from telegram import Bot

from app import services
from app.core.config import settings
from app.core.telegram.helpers import helpers
from app.core.telegram.messages import SupportBotMessage


async def send_lead_pay_notification_to_support_bot_handler(db: Session, order_id: int, lang: str):
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    message = SupportBotMessage.PAY_ORDER_NOTIFICATION[lang].format(
        order_number=order.order_number)

    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text=message,
        parse_mode="HTML"
    )


async def send_shop_bot_connection_notification_handler(
        db: Session, shop_telegram_bot_id: int, lang):

    shop_telegram_bot = services.shop.shop_telegram_bot.get(
        db, id=shop_telegram_bot_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)

    text = helpers.load_message(
        lang, "shop_connection", shop_title=shop_telegram_bot.shop.title,
        bot_username=shop_telegram_bot.telegram_bot.username
    )
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    text = helpers.load_message(
        lang, "support_welcome_notification",
    )
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    return


async def send_expiration_soon_notification(db: Session, lang):
    shops = helpers.get_expires_close_shops(db)
    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    for shop in shops:
        days = (shop["expires_at"] - datetime.now()).days
        text = SupportBotMessage.EXPIRATION_NOTIFICATION[lang].format(days=days)
        await bot.send_message(chat_id=shop["chat_id"], text=text)
    return

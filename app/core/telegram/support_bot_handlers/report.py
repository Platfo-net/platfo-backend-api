
from datetime import date

import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import services
from app.constants.currency import Currency
from app.core.config import settings
from app.core.telegram import helpers


async def send_shop_order_report(
        db: Session, lang: str, shop_id: int,
        amount: float, currency: str, count: int, date: date):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop_id)

    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return
    jdate = helpers.get_jalali_date_str(date)
    text = helpers.load_message(
        lang, "shop_daily_report",
        date=jdate,
        amount=helpers.number_to_price(int(amount)),
        currency=Currency.items[currency]["value"],
        count=count,
    )
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    message: telegram.Message = await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)

    return message.message_id

from pydantic import UUID4
import telegram
from app import services
from app.core.config import settings
from app.core.telegram import helpers
from telegram import Bot
from sqlalchemy.orm import Session


def get_shop_menu(bot_id: UUID4, lead_id: UUID4):
    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text="View Shop",
                web_app=telegram.WebAppInfo(f"{settings.PLATFO_SHOPS_BASE_URL}/{bot_id}/{lead_id}")
            )
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup


async def send_lead_order_to_bot_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):

    telegram_bot = services.telegram_bot.get(db, id=telegram_bot_id)
    if not telegram_bot:
        return
    lead = services.social.telegram_lead.get(db, id=lead_id)
    if not lead:
        return
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead.id != order.lead_id:
        return

    if lead.telegram_bot_id != telegram_bot.id:
        return

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    text = helpers.load_message(lang, "new_order", amount=amount, order=order)

    bot = Bot(token=telegram_bot.bot_token)
    await bot.send_message(chat_id=lead.chat_id, text=text)
    return

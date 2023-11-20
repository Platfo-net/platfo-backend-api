import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import services
from app.core.telegram.helpers import helpers
from app.core.telegram.messages import SupportBotMessage


async def verify_support_account(db: Session, update: telegram.Update,
                                 shop_telegram_bot_uuid: UUID4, lang: str):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_uuid(
        db, uuid=shop_telegram_bot_uuid)
    if not shop_telegram_bot_uuid:
        return await update.message.reply_text(
            text=SupportBotMessage.ACCOUNT_NOT_REGISTER[lang], parse_mode="HTML")

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    services.shop.shop_telegram_bot.verify_support_account(db, db_obj=shop_telegram_bot)
    text = helpers.load_message(lang, "support_account_connection_successfully",
                                shop_title=shop_telegram_bot.shop.title)
    await update.message.reply_text(
        text=text, parse_mode="HTML"
    )
    await update.message.edit_reply_markup(reply_markup=telegram.InlineKeyboardMarkup([]))

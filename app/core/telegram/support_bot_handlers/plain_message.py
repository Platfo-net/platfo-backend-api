
import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.core import security
from app.core.config import settings
from app.core.telegram.helpers import helpers
from app.core.telegram.messages import SupportBotMessage

from .order import send_order


def verify_shop_support_account_message(shop_telegram_bot: models.shop.ShopShopTelegramBot,
                                        lang: str):
    text = helpers.load_message(lang, "support_account_connection_confirmation",
                                shop_title=shop_telegram_bot.shop.title)
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT['command']}:{shop_telegram_bot.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return text, reply_markup


async def send_direct_message_helper(
        db: Session, update: telegram.Update, lead_id, lang):
    lead = services.social.telegram_lead.get(db, id=int(lead_id))
    if not lead:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=lead.telegram_bot_id)

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    message = helpers.load_message(lang, "direct_message_lead_id", lead_number=lead.lead_number)

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )

    message = helpers.load_message(lang, "direct_message_template", lead_number=lead.lead_number)

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


async def send_direct_message(
        db: Session, update: telegram.Update, lang: str):

    message = update.message.text
    chat_id = update.message.chat_id
    lead_number = message.split("\n")[0][1:]
    message = "\n".join(message.split("\n")[1:])

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(db, chat_id=chat_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    shop_bot = Bot(token=security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    lead = services.social.telegram_lead.get_by_lead_number_and_telegram_bot_id(
        db, lead_number=int(lead_number), telegram_bot_id=shop_telegram_bot.telegram_bot_id)

    if not lead:
        await bot.send_message(
            chat_id=shop_telegram_bot.support_account_chat_id,
            text=SupportBotMessage.INVALID_LEAD[lang])
        return

    text = helpers.load_message(lang, "support_direct_message", message=message)

    try:
        res: telegram.Message = await shop_bot.send_message(chat_id=lead.chat_id, text=text)
        await bot.send_message(
            chat_id=shop_telegram_bot.support_account_chat_id,
            text=SupportBotMessage.DIRECT_MESSAGE_SEND_SUCCESSFULLY[lang])

    except telegram.error.Forbidden:
        text = helpers.load_message(
            lang, "bot_block_warning",
            lead_number=lead.lead_number,
        )
        await update.message.reply_text(text=text)
        return

    reply_to_id = None
    if update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
    obj_in = schemas.social.TelegramLeadMessageCreate(
        lead_id=lead.id,
        is_lead_to_bot=False,
        message=message,
        message_id=update.message.id,
        mirror_message_id=res.message_id,
        reply_to_id=reply_to_id,
    )
    services.social.telegram_lead_message.create(db, obj_in=obj_in)
    return


async def plain_message_handler(db: Session, update: telegram.Update, lang: str):
    message = update.message.text.lstrip().rstrip()

    if not len(message):
        await update.message.reply_text(
            SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
        return

    elif update.message.text.isnumeric():
        order_number = int(update.message.text)
        await send_order(db, update, order_number, lang)
        return

    elif message[0] == "#":
        await send_direct_message(
            db, update, lang)
        return

    elif len(message) > 10:
        await update.message.reply_text(SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
        return

    elif message[0] == "P":
        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
            db, chat_id=update.message.chat_id)
        if shop_telegram_bot:
            await update.message.reply_text(
                SupportBotMessage.SUPPORT_ACCOUNT_ALREADY_CONNECTED[lang].format(
                    title=shop_telegram_bot.shop.title),
                parse_mode="HTML"
            )
            return

        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=message)

        if not shop_telegram_bot:
            text = helpers.load_message(lang, "support_account_connection_wrong_code")
            await update.message.reply_text(text, parse_mode="HTML")
            return

        if shop_telegram_bot.support_account_chat_id:
            await update.message.reply_text(
                SupportBotMessage.SHOP_ALREADY_CONNECTED[lang].format(
                    title=shop_telegram_bot.shop.title), parse_mode="HTML"
            )
            return

        text, reply_markup = verify_shop_support_account_message(
            shop_telegram_bot, lang)

        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )
        services.shop.shop_telegram_bot.set_support_account_chat_id(
            db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)
        return
    update.message.reply_text(text=SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
    return

import asyncio

import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import schemas, services
from app.core.celery import celery
from app.core.config import settings
from app.db.session import SessionLocal


@celery.task
def telegram_support_bot_task(data):
    db = SessionLocal()
    try:
        asyncio.run(telegram_support_bot_handler(db, data))
    except Exception:
        pass

    db.close()


@celery.task
def telegram_webhook_task(data: dict, bot_id: int):
    db = SessionLocal()
    try:
        asyncio.run(telegram_bot_webhook_handler(db, data, bot_id=bot_id))
    except Exception as e:
        print(e)

    db.close()


async def telegram_support_bot_handler(db: Session, data: dict):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    update: telegram.Update = telegram.Update.de_json(data, bot=bot)
    if update.message.text == "/start":
        await update.message.reply_text("Enter your code")
    else:
        code = update.message.text.lstrip().rstrip()
        if len(code) != 8:
            await update.message.reply_text("Wrong code.")
            return
        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=code)
        if not shop_telegram_bot:
            await update.message.reply_text("Wrong code.")
            return
        if shop_telegram_bot.is_support_verified:
            await update.message.reply_text(
                f"Your shop '{shop_telegram_bot.shop.title}' is"
                " already connected to an account.")
            return

        await update.message.reply_text(
            f"You are trying to connect your account to {shop_telegram_bot.shop.title} shop,\n"
            f"Enter this code in app: {shop_telegram_bot.support_bot_token}"
        )
        services.shop.shop_telegram_bot.set_support_account_chat_id(
            db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)


async def telegram_bot_webhook_handler(db: Session, data: dict, bot_id: int):
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)

    if not shop_telegram_bot:
        return

    user = data["message"]["from"]
    lead = services.social.telegram_lead.get_by_chat_id(db, chat_id=user.get("id"))
    if not lead:
        services.social.telegram_lead.create(
            db,
            obj_in=schemas.social.TelegramLeadCreate(
                telegram_bot_id=shop_telegram_bot.telegram_bot_id,
                chat_id=user.get("id"),
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                username=user.get("username"),
            )
        )
    bot = Bot(token=telegram_bot.bot_token)
    update = telegram.Update.de_json(data, bot)

    await update.message.reply_text(
        text=f"Hi, you are using `{shop_telegram_bot.shop.title}` shop",
        reply_markup=get_shop_menu(telegram_bot.uuid, shop_telegram_bot.shop.uuid)
    )


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

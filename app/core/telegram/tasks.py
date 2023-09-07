from telegram import Bot
import asyncio
import telegram
from app import services
from app.core.config import settings
from app.db.session import SessionLocal
from app.core.celery import celery


@celery.task
def telegram_support_bot_task(data):
    asyncio.run(telegram_support_bot_handler(data))


async def telegram_support_bot_handler(data):
    db = SessionLocal()
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    update: telegram.Update = telegram.Update.de_json(data, bot=bot)
    if update.message.text == "/start":
        await update.message.reply_text("Enter your code")
    else:
        code = update.message.text.lstrip().rstrip()
        if len(code) != 8:
            await update.message.reply_text(f"Wrong code.")
            return
        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=code)
        if not shop_telegram_bot:
            await update.message.reply_text(f"Wrong code.")
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


async def telegram_bot_webhook_handler(data, bot_id):
    db = SessionLocal()
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)
    if not shop_telegram_bot:
        return
    bot = Bot(token=telegram_bot.bot_token)
    update = telegram.Update.de_json(data, bot)
    await update.message.reply_text(text=f"Hi, you are using `{shop_telegram_bot.shop.title}` shop" , reply_markup = get_menu(shop_telegram_bot.shop.title))
    db.close()


def get_menu(shop_name):
    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text="View Shop", web_app=telegram.WebAppInfo(f"https://api.platfo.net/sample-shop/{shop_name}"))
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup

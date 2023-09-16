from telegram import Bot
import telegram
from app.core.config import settings


async def send_message(message, chat_id):
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(message, chat_id=chat_id)


async def set_support_bot_webhook():
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    m = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/webhook/telegram/support-bot"


    await bot.set_webhook(
        f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/webhook/telegram/support-bot"
    )
    await bot.set_my_commands(
        commands = [
            telegram.BotCommand("/paid_orders"),
            telegram.BotCommand("/accepted_orders"),
        ]
        
    )
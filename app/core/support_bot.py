from telegram import Bot

from app.core.config import settings


async def send_message(message, chat_id):
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(message, chat_id=chat_id)

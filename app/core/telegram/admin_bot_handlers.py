import telegram
from sqlalchemy.orm import Session

from app import services
from app.core.config import settings


async def send_create_shop_notification_to_all_admins_handler(
        db: Session, shop_id: int, lang: str):
    bot = telegram.Bot(settings.TELEGRAM_ADMIN_BOT_TOKEN)
    shop = services.shop.shop.get(db, id=shop_id)
    admin_users = services.user.get_telegram_admin_multi(db)
    for user in admin_users:
        await bot.send_message(text=f"shop {shop.title} created.",
                               chat_id=user.telegram_admin_bot_chat_id)


async def send_register_user_notification_to_all_admins_handler(
        db: Session, user_id: int, lang: str):
    bot = telegram.Bot(settings.TELEGRAM_ADMIN_BOT_TOKEN)
    user = services.user.get(db, id=user_id)
    admin_users = services.user.get_telegram_admin_multi(db)
    for admin in admin_users:
        await bot.send_message(text=f"user {user.phone_number} registered.",
                               chat_id=admin.telegram_admin_bot_chat_id)

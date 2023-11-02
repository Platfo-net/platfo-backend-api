import telegram
from sqlalchemy.orm import Session

from app import services
from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.core.config import settings


async def accept_credit_extending(
        db: Session, update: telegram.Update, shop_telegram_payment_record_id: int, lang):
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.get(
        db, id=shop_telegram_payment_record_id)
    credit = services.credit.shop_credit.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    services.credit.shop_credit.add_shop_credit(
        db, db_obj=credit, days=shop_telegram_payment_record.plan.extend_days
    )

    services.credit.shop_telegram_payment_record.change_status(
        db, db_obj=shop_telegram_payment_record, status=ShopTelegramPaymentRecordStatus.APPLIED)

    await update.message.reply_text("باشه", parse_mode="HTML")

    support_bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    await support_bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text="حساب شما شارژ شد",
        reply_to_message_id=shop_telegram_payment_record.payment_message_id,
    )


async def decline_credit_extending(
    db: Session,
    update: telegram.Update,
    shop_telegram_payment_record_id: int,
    lang
):
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.get(
        db, id=shop_telegram_payment_record_id)
    services.credit.shop_telegram_payment_record.change_status(
        db, db_obj=shop_telegram_payment_record, status=ShopTelegramPaymentRecordStatus.DECLINED)

    await update.message.reply_text("باشه", parse_mode="HTML")

    support_bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    await support_bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text="حساب شما شارژ نشد",
        reply_to_message_id=shop_telegram_payment_record.payment_message_id,
    )


async def send_create_shop_notification_to_all_admins_handler(
        db: Session, shop_id: int, lang: str):
    bot = telegram.Bot(settings.TELEGRAM_ADMIN_BOT_TOKEN)
    shop = services.shop.shop.get(db, id=shop_id)
    admin_users = services.user.get_telegram_admin_multi(db)
    for user in admin_users:
        await bot.send_message(text=f"shop {shop.title} created.",
                               chat_id=user.telegram_admin_bot_chat_id)

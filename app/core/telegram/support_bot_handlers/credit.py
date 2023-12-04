
import os

import jdatetime
import pytz
import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from suds.client import Client
from telegram import Bot

from app import models, services
from app.constants.currency import Currency
from app.constants.module import Module
from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.core.config import settings
from app.core.telegram import helpers
from app.core.telegram.messages import SupportBotMessage


async def handle_credit_extending(db: Session, update: telegram.Update, lang: str):
    plans = services.credit.plan.get_multi(
        db, currency=Currency.IRT["value"], module=Module.TELEGRAM_SHOP)
    keyboard = []
    items = []
    for plan in plans:
        keyboard.append([
            telegram.InlineKeyboardButton(
                plan.title,
                callback_data=f"{TelegramCallbackCommand.CREDIT_PLAN['command']}:{plan.id}")  # noqa
        ])
        items.append(
            {
                "price": helpers.number_to_price(int(plan.discounted_price)),
                "title": plan.title
            }
        )
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    text = helpers.load_message(lang, "credit_shop_pricing",
                                items=items, currency=Currency.IRT["name"])

    await update.message.reply_text(parse_mode="HTML", text=text, reply_markup=reply_markup)


async def handle_credit_plan(
    db: Session,
    update: telegram.Update,
    plan_id: UUID4,
    lang: str,
    shop_id: int,
):
    plan = services.credit.plan.get(db, plan_id)
    text = helpers.load_message(
        lang, "credit_shop_plan",
        amount=helpers.number_to_price(int(plan.discounted_price)),
        currency=Currency.IRT["name"]
    )
    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.create(
        db,
        shop_id=shop_id,
        plan_id=plan.id,
    )
    result = zarrin_client.service.PaymentRequest(
        settings.ZARINPAL_MERCHANT_ID,
        plan.discounted_price * 10,
        "افزایش اعتبار فروشگاه",
        "",
        "",
        f"{settings.SERVER_ADDRESS_NAME}/{settings.API_V1_STR}/credit/shop/telegram/{shop_telegram_payment_record.id}/verify"  # noqa
    )
    # TODO handle status of zarrin
    services.credit.shop_telegram_payment_record.add_authority(
        db, db_obj=shop_telegram_payment_record, authority=result.Authority)

    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text="پرداخت",
                web_app=telegram.WebAppInfo(
                    f"{settings.ZARINPAL_BASE_URL}/{result.Authority}"
                )
            )
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=text, reply_markup=reply_markup)


async def handle_shop_credit_extending(
    db: Session,
    message: telegram.Message,
    bucket,
    shop_id: int,
    lang: str,
):
    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.\
        get_by_shop_and_reply_to_message_id(
            db, shop_id=shop_id, reply_to_message_id=message.reply_to_message.message_id
        )
    if not shop_telegram_payment_record:
        return
    photo_unique_id = message.photo[-1].file_id
    url, file_name = await helpers.download_and_upload_telegram_image(
        bot, photo_unique_id, bucket)
    if not url:
        await message.reply_text(text="Error in processing image")
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.add_payment_image(
        db, db_obj=shop_telegram_payment_record, image_name=file_name,
        message_id=message.message_id)

    services.credit.shop_telegram_payment_record.change_status(
        db, db_obj=shop_telegram_payment_record,
        status=ShopTelegramPaymentRecordStatus.PAID
    )

    await message.reply_text(SupportBotMessage.CREDIT_EXTENDING_ADMIN_CHECK[lang])
    admin_user = services.user.get_telegram_payment_admin(db)
    admin_bot = telegram.Bot(settings.TELEGRAM_ADMIN_BOT_TOKEN)
    text = helpers.load_message(
        lang,
        "admin_bot_credit_approve",
        plan_title=shop_telegram_payment_record.plan.title
    )

    await admin_bot.send_photo(
        chat_id=admin_user.telegram_admin_bot_chat_id,
        caption=text,
        photo=url,
        reply_markup=helpers.get_admin_credit_charge_reply_markup(shop_telegram_payment_record)
    )
    os.remove(file_name)
    return


async def send_user_credit_information(
    db: Session,
    update: telegram.Update,
    shop_telegram_bot: models.shop.ShopShopTelegramBot,
    lang: str
):
    shop_credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_telegram_bot.shop_id)
    if not shop_credit:
        return
    iran_tz = pytz.timezone("Asia/Tehran")
    expires_at_datetime = shop_credit.expires_at.astimezone(iran_tz)
    jalali_date = jdatetime.GregorianToJalali(
        expires_at_datetime.year, expires_at_datetime.month, expires_at_datetime.day)
    date_str = f"{jalali_date.jyear}/{jalali_date.jmonth}/{jalali_date.jday}"
    time_str = f"{expires_at_datetime.hour}:{expires_at_datetime.minute}"

    text = helpers.load_message(lang, "shop_credit_view", date_str=date_str, time_str=time_str)
    await update.message.reply_text(text=text)

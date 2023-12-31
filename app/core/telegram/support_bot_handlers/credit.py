
import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from suds.client import Client

from app import models, services
from app.constants.currency import Currency
from app.constants.module import Module
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.core.config import settings
from app.core.telegram import helpers


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
    shop = services.shop.shop.get(db, id=shop_id)
    if not shop:
        return
    email = shop.user.email
    phone_number = "0f{shop.user.phone_number}"

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
        amount=plan.discounted_price
    )
    callback = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/credit/credit/shop/telegram/{shop_telegram_payment_record.id}/verify"  # noqa
    result = zarrin_client.service.PaymentRequest(
        settings.ZARINPAL_MERCHANT_ID,
        plan.discounted_price,
        "افزایش اعتبار فروشگاه",
        email,
        phone_number,
        callback,
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


async def send_user_credit_information(
    db: Session,
    update: telegram.Update,
    shop_telegram_bot: models.shop.ShopShopTelegramBot,
    lang: str
):
    shop_credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop_telegram_bot.shop_id)
    if not shop_credit:
        return
    date_str, time_str = helpers.get_credit_str(shop_credit.expires_at)

    text = helpers.load_message(lang, "shop_credit_view", date_str=date_str, time_str=time_str)
    await update.message.reply_text(text=text)

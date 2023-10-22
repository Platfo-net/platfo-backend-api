import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import services
from app.constants.currency import Currency
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.core import security
from app.core.config import settings
from app.core.telegram import helpers

VITRIN = {
    "fa": "ویترین",
}


def get_shop_menu(shop_id: UUID4, lead_id: UUID4, lang: str):
    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text=VITRIN[lang],
                web_app=telegram.WebAppInfo(
                    f"{settings.PLATFO_SHOPS_BASE_URL}/{shop_id}/{lead_id}")
            )
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup


async def send_lead_order_to_bot_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):

    telegram_bot = services.telegram_bot.get(db, id=telegram_bot_id)
    if not telegram_bot:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot_id)

    if not helpers.has_credit_by_shop_id(db, shop_id=shop_telegram_bot.shop_id):
        return
    lead = services.social.telegram_lead.get(db, id=lead_id)
    if not lead:
        return
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead.id != order.lead_id:
        return

    if lead.telegram_bot_id != telegram_bot.id:
        return
    items = []

    amount = 0
    for item in order.items:
        amount += item.count * item.price
        items.append({
            "price": helpers.number_to_price(item.price),
            "title": item.title,
            "count": item.count,

        })
    currency = Currency.IRR["name"]

    text = helpers.load_message(
        lang, "lead_new_order",
        amount=helpers.number_to_price(int(amount)),
        order=order,
        items=items,
        order_status=OrderStatus.items[order.status]["title"][lang],
        payment_method=PaymentMethod.items[order.shop_payment_method.payment_method.title][lang],
        currency=currency,
    )
    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))
    order_message: telegram.Message = await bot.send_message(
        chat_id=lead.chat_id, text=text, parse_mode="HTML")

    shop_payment_method = services.shop.shop_payment_method.get(
        db, id=order.shop_payment_method_id)
    # TODO handle other payment methods later
    text = helpers.load_message(
        lang,
        "card_transfer_payment_notification",
        amount=helpers.number_to_price(int(amount)),
        currency=currency,
        card_number=shop_payment_method.information["card_number"],
        name=shop_payment_method.information["name"],
        bank=shop_payment_method.information.get("bank", "")
    )

    payment_info_message: telegram.Message = await bot.send_message(
        chat_id=lead.chat_id, text=text, parse_mode="HTML")

    return order_message.message_id, payment_info_message.message_id

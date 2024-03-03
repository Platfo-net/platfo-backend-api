import telegram
from pydantic import UUID4

from app import models
from app.constants.currency import Currency
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.core.config import settings
from app.core.telegram.helpers import helpers

VITRIN = {
    "fa": "ویترین",
}


def get_order_message(order: models.shop.ShopOrder, lang, amount):
    payment_method = PaymentMethod.CARD_TRANSFER[lang]
    if order.shop_payment_method:
        payment_method = PaymentMethod.items[order.shop_payment_method.payment_method.title][lang]

    items = []

    for item in order.items:
        items.append({
            "price": helpers.number_to_price(int(item.price)),
            "title": item.product.title,
            "count": item.count,
        })

    text = helpers.load_message(
        lang, "order",
        amount=helpers.number_to_price(int(amount)),
        order=order,
        order_status=OrderStatus.items[order.status]["title"][lang],
        lead_number=order.lead.lead_number,
        currency=Currency.IRT["name"],
        payment_method=payment_method,
        items=items,
    )

    return text


def get_start_support_bot_message(lang):
    return helpers.load_message(lang, "start_support_bot")


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


def get_bot_menu(button_name: str, app_link: str):
    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text=button_name,
                web_app=telegram.WebAppInfo(app_link)
            )
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup

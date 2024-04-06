from typing import Callable

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
from app.core.telegram.messages import SupportBotMessage


async def send_order(db: Session, update: telegram.Update, order_number: int, lang: str):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
        db, chat_id=update.message.chat_id)

    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    order = services.shop.order.get_by_order_number_and_shop_id(
        db, order_number=order_number, shop_id=shop_telegram_bot.shop_id)

    if not order:
        await update.message.reply_text(
            SupportBotMessage.ORDER_NOT_FOUND["fa"].format(order_number=order_number),
            parse_mode="HTML"
        )
        return

    amount = 0
    items = []
    for item in order.items:
        amount += item.price * item.count
        items.append({
            "price": helpers.number_to_price(int(item.price)),
            "title": item.product.title,
            "count": item.count,
        })

    payment_method = PaymentMethod.items[order.shop_payment_method.payment_method.title][lang]
    shipment_method = order.shipment_method
    reply_markup = telegram.InlineKeyboardMarkup([])
    order_status = ""
    amount += shipment_method.price

    if order.status == OrderStatus.PAYMENT_CHECK["value"]:
        reply_markup = helpers.get_payment_check_order_reply_markup(order, lang)
        order_status = OrderStatus.PAYMENT_CHECK["title"][lang]
    elif order.status == OrderStatus.ACCEPTED["value"]:
        reply_markup = helpers.get_accepted_order_reply_markup(order, lang)
        order_status = OrderStatus.ACCEPTED["title"][lang]
    elif order.status == OrderStatus.PREPARATION["value"]:
        reply_markup = helpers.get_prepare_order_reply_markup(order, lang)
        order_status = OrderStatus.PREPARATION["title"][lang]
    elif order.status == OrderStatus.UNPAID["value"]:
        reply_markup = helpers.get_unpaid_order_reply_markup(order, lang)
        order_status = OrderStatus.UNPAID["title"][lang]
    elif order.status == OrderStatus.DECLINED["value"]:
        reply_markup = helpers.get_declined_order_reply_markup(order, lang)
        order_status = OrderStatus.DECLINED["title"][lang]
    elif order.status == OrderStatus.SENT["value"]:
        reply_markup = helpers.get_empty_reply_markup(order, lang)
        order_status = OrderStatus.SENT["title"][lang]
    elif order.status == OrderStatus.PAYMENT_DECLINED["value"]:
        reply_markup = helpers.get_empty_reply_markup(order, lang)
        order_status = OrderStatus.PAYMENT_DECLINED["title"][lang]

    text = helpers.load_message(
        lang, "order",
        amount=helpers.number_to_price(int(amount)),
        order=order,
        order_status=order_status,
        currency=Currency.IRT["name"],
        items=items,
        shipment_method_title=shipment_method.title,
        shipment_method_price=helpers.number_to_price(int(shipment_method.price)),
        payment_method=payment_method,
        table_title=None if not order.table_id else order.table.title
    )

    await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode="HTML")


async def send_order_detail(db: Session, update: telegram.Update, order_uuid: UUID4, lang: str):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
        db, chat_id=update.message.chat_id)

    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    order = services.shop.order.get_by_uuid(
        db, uuid=order_uuid)

    if not order:
        return

    text = helpers.load_message(
        lang, "order_detail",
        order=order,
        table_title=None if not order.table_id else order.table.title
    )
    await update.message.reply_text(
        text=text,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )


async def order_change_status_handler(
        db: Session,
        update: telegram.Update,
        order_id,
        lang,
        status,
        action_message,
        get_reply_markup
):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(
        db, order=order, status=status["value"])

    message = action_message[lang].format(order_number=order.order_number)

    amount = 0
    items = []

    for item in order.items:
        amount += item.count * item.price
        items.append({
            "price": helpers.number_to_price(int(item.price)),
            "title": item.product.title,
            "count": item.count,
        })
    amount += order.shipment_cost_amount

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )
    await update.message.edit_text(
        text=helpers.get_order_message(order, lang, amount),
        reply_markup=get_reply_markup(order, lang),
        parse_mode="HTML"
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)

    bot = Bot(token=security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    text = helpers.load_message(
        lang, "order_change_status_notification",
        order_status=OrderStatus.items[order.status]["title"][lang],
        order_number=order.order_number,
    )
    try:
        await bot.send_message(chat_id=order.lead.chat_id, text=text)
    except telegram.error.Forbidden:
        text = helpers.load_message(
            lang, "bot_block_warning",
            lead_number=order.lead.lead_number,
        )
        update.message.reply_text(text=text)


async def send_lead_order_to_shop_support_bot(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    lead = services.social.telegram_lead.get(db, id=lead_id)

    if lead and lead.telegram_bot_id != shop_telegram_bot.telegram_bot_id:
        return

    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead and lead.id != order.lead_id:
        return

    amount = 0
    items = []
    for item in order.items:
        amount += item.count * item.price
        items.append({
            "price": helpers.number_to_price(int(item.price)),
            "title": item.product.title,
            "count": item.count,
        })
    amount += order.shipment_cost_amount

    payment_method = PaymentMethod.items[order.shop_payment_method.payment_method.title][lang]

    text = helpers.load_message(
        lang, "support_new_order",
        amount=helpers.number_to_price(int(amount)),
        order=order,
        lead_number=lead.lead_number if lead else "",
        order_status=OrderStatus.items[order.status]["title"][lang],
        currency=Currency.IRT["name"],
        payment_method=payment_method,
        items=items,
        table_title=None if not order.table_id else order.table.title
    )
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    message: telegram.Message = await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    return message.message_id


async def send_all_order_by_status(
        db: Session, update: telegram.Update, status: str,
        get_message: Callable, get_reply_markup: Callable, lang: str
):
    chat_id = update.message.chat_id
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
        db, chat_id=chat_id)

    if not shop_telegram_bot:
        await update.message.reply_text(
            text=SupportBotMessage.ACCOUNT_NOT_REGISTER[lang],
            parse_mode="HTML",
        )
        return

    orders = services.shop.order.get_shop_orders(db, shop_id=shop_telegram_bot.shop_id,
                                                 status=[status["value"]])  # noqa

    for order in orders:
        amount = 0
        for item in order.items:
            amount += item.price * item.count
        amount += order.shipment_cost_amount

        text = get_message(order, lang, amount)
        reply_markup = get_reply_markup(
            order, lang)
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML",
        )

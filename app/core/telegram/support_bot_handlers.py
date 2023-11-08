import os
from datetime import datetime
from typing import Callable

import jdatetime
import pytz
import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.currency import Currency
from app.constants.module import Module
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.core import security
from app.core.config import settings
from app.core.support_bot import set_support_bot_webhook
from app.core.telegram import helpers
from app.core.telegram.messages import SupportBotMessage


async def plain_message_handler(db: Session, update: telegram.Update, lang: str):
    message = update.message.text.lstrip().rstrip()

    if not len(message):
        await update.message.reply_text(
            SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
        return

    elif update.message.text.isnumeric():
        order_number = int(update.message.text)
        await send_order(db, update, order_number, lang)
        return

    elif message[0] == "#":
        await send_direct_message(
            db, update, lang)
        return

    elif len(message) > 10:
        await update.message.reply_text(SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
        return

    elif message[0] == "P":
        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
            db, chat_id=update.message.chat_id)
        if shop_telegram_bot:
            await update.message.reply_text(
                SupportBotMessage.SUPPORT_ACCOUNT_ALREADY_CONNECTED[lang].format(
                    title=shop_telegram_bot.shop.title),
                parse_mode="HTML"
            )
            return

        shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=message)

        if not shop_telegram_bot:
            text = helpers.load_message(lang, "support_account_connection_wrong_code")
            await update.message.reply_text(text, parse_mode="HTML")
            return

        if shop_telegram_bot.support_account_chat_id:
            await update.message.reply_text(
                SupportBotMessage.SHOP_ALREADY_CONNECTED[lang].format(
                    title=shop_telegram_bot.shop.title), parse_mode="HTML"
            )
            return

        text, reply_markup = verify_shop_support_account_message(
            shop_telegram_bot, lang)

        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML"
        )
        services.shop.shop_telegram_bot.set_support_account_chat_id(
            db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)
        return
    update.message.reply_text(text=SupportBotMessage.INVALID_COMMAND[lang], parse_mode="HTML")
    return


async def send_lead_pay_notification_to_support_bot_handler(db: Session, order_id: int, lang: str):
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    message = SupportBotMessage.PAY_ORDER_NOTIFICATION[lang].format(
        order_number=order.order_number)

    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text=message,
        parse_mode="HTML"
    )


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

    reply_markup = telegram.InlineKeyboardMarkup([])
    text = ""

    if order.status == OrderStatus.PAYMENT_CHECK["value"]:
        reply_markup = get_payment_check_order_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.PAYMENT_CHECK["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.ACCEPTED["value"]:
        reply_markup = get_accepted_order_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.ACCEPTED["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.PREPARATION["value"]:
        reply_markup = get_prepare_order_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.PREPARATION["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.UNPAID["value"]:
        reply_markup = get_unpaid_order_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.UNPAID["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.DECLINED["value"]:
        reply_markup = get_declined_order_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.DECLINED["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.SENT["value"]:
        reply_markup = get_empty_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.SENT["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
        )

    elif order.status == OrderStatus.PAYMENT_DECLINED["value"]:
        reply_markup = get_empty_reply_markup(order, lang)
        text = helpers.load_message(
            lang, "order",
            amount=helpers.number_to_price(int(amount)),
            order=order,
            order_status=OrderStatus.PAYMENT_DECLINED["title"][lang],
            currency=Currency.IRT["name"],
            items=items,
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
        db, id=order_uuid)

    if not order:
        return

    text = helpers.load_message(lang, "order_detail", order=order)
    await update.message.reply_text(
        text=text,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )


async def verify_support_account(db: Session, update: telegram.Update,
                                 shop_telegram_bot_uuid: UUID4, lang: str):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_uuid(
        db, uuid=shop_telegram_bot_uuid)
    if not shop_telegram_bot_uuid:
        return await update.message.reply_text(
            text=SupportBotMessage.ACCOUNT_NOT_REGISTER[lang], parse_mode="HTML")

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    services.shop.shop_telegram_bot.verify_support_account(db, db_obj=shop_telegram_bot)
    text = helpers.load_message(lang, "support_account_connection_successfully",
                                shop_title=shop_telegram_bot.shop.title)
    await update.message.reply_text(
        text=text, parse_mode="HTML"
    )
    await update.message.edit_reply_markup(reply_markup=telegram.InlineKeyboardMarkup([]))


def verify_shop_support_account_message(shop_telegram_bot: models.shop.ShopShopTelegramBot,
                                        lang: str):
    text = helpers.load_message(lang, "support_account_connection_confirmation",
                                shop_title=shop_telegram_bot.shop.title)
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT['command']}:{shop_telegram_bot.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return text, reply_markup


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

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )
    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=get_reply_markup(order, lang),
        parse_mode="HTML"
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)

    bot = Bot(token=security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    text = helpers.load_message(
        lang, "order_change_status_notification",
        order_status=OrderStatus.items[order.status]["title"][lang],
        order_number=order.order_number
    )
    try:
        await bot.send_message(chat_id=order.lead.chat_id, text=text)
    except telegram.error.Forbidden:
        text = helpers.load_message(
            lang, "bot_block_warning",
            lead_number=order.lead.lead_number,
        )
        update.message.reply_text(text=text)


async def send_direct_message_helper(
        db: Session, update: telegram.Update, lead_id, lang):
    lead = services.social.telegram_lead.get(db, id=int(lead_id))
    if not lead:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=lead.telegram_bot_id)

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    message = helpers.load_message(lang, "direct_message_lead_id", lead_number=lead.lead_number)

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )

    message = helpers.load_message(lang, "direct_message_template", lead_number=lead.lead_number)

    await update.message.reply_text(
        message,
        parse_mode="HTML",
    )


async def send_lead_order_to_shop_support_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    lead = services.social.telegram_lead.get(db, id=lead_id)
    if not lead:
        return

    if lead.telegram_bot_id != shop_telegram_bot.telegram_bot_id:
        return

    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead.id != order.lead_id:
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

    payment_method = PaymentMethod.items[order.shop_payment_method.payment_method.title][lang]

    text = helpers.load_message(
        lang, "support_new_order",
        amount=helpers.number_to_price(int(amount)),
        order=order,
        lead_number=lead.lead_number,
        order_status=OrderStatus.items[order.status]["title"][lang],
        currency=Currency.IRT["name"],
        payment_method=payment_method,
        items=items,
    )
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    message: telegram.Message = await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    return message.message_id


async def send_shop_bot_connection_notification_handler(
        db: Session, shop_telegram_bot_id: int, lang):

    shop_telegram_bot = services.shop.shop_telegram_bot.get(
        db, id=shop_telegram_bot_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return

    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)

    text = helpers.load_message(
        lang, "shop_connection", shop_title=shop_telegram_bot.shop.title,
        bot_username=shop_telegram_bot.telegram_bot.username
    )
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    text = helpers.load_message(
        lang, "support_welcome_notification",
    )
    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    return


async def send_direct_message(
        db: Session, update: telegram.Update, lang: str):

    message = update.message.text
    chat_id = update.message.chat_id
    lead_number = message.split("\n")[0][1:]
    message = "\n".join(message.split("\n")[1:])

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(db, chat_id=chat_id)
    if not shop_telegram_bot:
        return

    if not helpers.has_credit_by_shop_id(db, shop_telegram_bot.shop_id):
        return
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    shop_bot = Bot(token=security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    lead = services.social.telegram_lead.get_by_lead_number_and_telegram_bot_id(
        db, lead_number=int(lead_number), telegram_bot_id=shop_telegram_bot.telegram_bot_id)

    if not lead:
        await bot.send_message(
            chat_id=shop_telegram_bot.support_account_chat_id,
            text=SupportBotMessage.INVALID_LEAD[lang])
        return

    text = helpers.load_message(lang, "support_direct_message", message=message)

    try:
        res: telegram.Message = await shop_bot.send_message(chat_id=lead.chat_id, text=text)
        await bot.send_message(
            chat_id=shop_telegram_bot.support_account_chat_id,
            text=SupportBotMessage.DIRECT_MESSAGE_SEND_SUCCESSFULLY[lang])

    except telegram.error.Forbidden:
        text = helpers.load_message(
            lang, "bot_block_warning",
            lead_number=lead.lead_number,
        )
        await update.message.reply_text(text=text)
        return

    reply_to_id = None
    if update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
    obj_in = schemas.social.TelegramLeadMessageCreate(
        lead_id=lead.id,
        is_lead_to_bot=False,
        message=message,
        message_id=update.message.id,
        mirror_message_id=res.message_id,
        reply_to_id=reply_to_id,
    )
    services.social.telegram_lead_message.create(db, obj_in=obj_in)
    return


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


def get_payment_check_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_ORDER['command']}:{order.uuid}"),
        ], [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.DECLINE_PAYMENT_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.DECLINE_PAYMENT_ORDER['command']}:{order.uuid}")  # noqa
        ], [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ORDER_DETAIL["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ORDER_DETAIL['command']}:{order.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_accepted_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.PREPARE_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.PREPARE_ORDER['command']}:{order.uuid}"),  # noqa
        ],
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_ORDER['command']}:{order.uuid}"),  # noqa
        ], [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ORDER_DETAIL["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ORDER_DETAIL['command']}:{order.uuid}")  # noqa
        ]
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_unpaid_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_ORDER['command']}:{order.uuid}"
            ),
        ],
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ORDER_DETAIL["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ORDER_DETAIL['command']}:{order.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_prepare_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_ORDER['command']}:{order.uuid}"
            ),  # noqa
        ], [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ORDER_DETAIL["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ORDER_DETAIL['command']}:{order.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_declined_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}"  # noqa
            ),  # noqa
        ], [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ORDER_DETAIL["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ORDER_DETAIL['command']}:{order.uuid}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


async def send_expiration_soon_notification(db: Session, lang):
    shops = helpers.get_expires_close_shops(db)
    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    for shop in shops:
        days = (shop["expires_at"] - datetime.now()).days
        text = SupportBotMessage.EXPIRATION_NOTIFICATION[lang].format(days=days)
        await bot.send_message(chat_id=shop["chat_id"], text=text)
    return


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

    orders = services.shop.order.get_shop_orders(db, shop_id=shop_telegram_bot.shop_id, status=[status["value"]])  # noqa

    for order in orders:
        amount = 0
        for item in order.items:
            amount += item.price * item.count
        text = get_message(order, lang, amount)
        reply_markup = get_reply_markup(
            order, lang)
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode="HTML",
        )


def get_start_support_bot_reply_markup(lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.NEW_CONNECTION["title"][lang],
                callback_data=f"{TelegramCallbackCommand.NEW_CONNECTION['command']}:#"  # noqa
            ),  # noqa
        ],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_start_support_bot_message(lang):
    return helpers.load_message(lang, "start_support_bot")


def get_empty_reply_markup(*args, **kwargs):
    return telegram.InlineKeyboardMarkup([])


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
    reply_to_message = await update.message.reply_text(text=text)
    services.credit.shop_telegram_payment_record.create(
        db,
        shop_id=shop_id,
        plan_id=plan.id,
        reply_to_message_id=reply_to_message.message_id,
    )


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
        reply_markup=get_admin_credit_charge_reply_markup(shop_telegram_payment_record)
    )
    os.remove(file_name)
    return


def get_admin_credit_charge_reply_markup(
        shop_telegram_payment_record: models.credit.CreditShopTelegramPaymentRecord
):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                "آره بابا. بدبخته",
                callback_data=f"{TelegramCallbackCommand.ACCEPT_CREDIT_EXTENDING['command']}:{shop_telegram_payment_record.id}")  # noqa
        ], [
            telegram.InlineKeyboardButton(
                "نوچ",
                callback_data=f"{TelegramCallbackCommand.DECLINE_CREDIT_EXTENDING['command']}:{shop_telegram_payment_record.id}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup


async def set_support_bot_commands_task_handler():
    await set_support_bot_webhook()


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

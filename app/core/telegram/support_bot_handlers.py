from datetime import datetime
from typing import Callable

import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.order_status import OrderStatus
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.core import security
from app.core.config import settings
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
    for item in order.items:
        amount += item.price * item.count

    reply_markup = telegram.InlineKeyboardMarkup([])
    text = ""

    if order.status == OrderStatus.PAYMENT_CHECK["value"]:
        reply_markup = get_payment_check_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.PAYMENT_CHECK["title"][lang])

    elif order.status == OrderStatus.ACCEPTED["value"]:
        reply_markup = get_accepted_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.ACCEPTED["title"][lang])

    elif order.status == OrderStatus.PREPARATION["value"]:
        reply_markup = get_prepare_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.PREPARATION["title"][lang])

    elif order.status == OrderStatus.UNPAID["value"]:
        reply_markup = get_unpaid_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.UNPAID["title"][lang])

    elif order.status == OrderStatus.DECLINED["value"]:
        reply_markup = get_declined_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.DECLINED["title"][lang])

    elif order.status == OrderStatus.SENT["value"]:
        reply_markup = get_send_order_reply_markup(order, lang)
        text = helpers.load_message(lang, "order", amount=amount, order=order,
                                    order_status=OrderStatus.SENT["title"][lang])

    await update.message.reply_text(text=text, reply_markup=reply_markup, parse_mode="HTML")


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


async def accept_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.ACCEPTED["value"])

    message = SupportBotMessage.ACCEPT_ORDER[lang].format(order_number=order.order_number)

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )
    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=get_accepted_order_reply_markup(order, lang),
        parse_mode="HTML"
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    bot = Bot(token=shop_telegram_bot.telegram_bot.bot_token)
    text = helpers.load_message(lang, "lead_order", order=order,
                                order_status=OrderStatus.items[order.status][lang], amount=amount)

    await bot.send_message(chat_id=order.lead.chat_id, text=text)


async def decline_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.DECLINED["value"])

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    message = SupportBotMessage.DECLINE_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML"
    )
    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=telegram.InlineKeyboardMarkup([]),
        parse_mode="HTML",
    )
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    bot = Bot(token=shop_telegram_bot.telegram_bot.bot_token)

    text = helpers.load_message(lang, "lead_order", order=order,
                                order_status=OrderStatus.items[order.status][lang], amount=amount)

    await bot.send_message(chat_id=order.lead.chat_id, text=text)


async def decline_payment_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(db, order=order, status=OrderStatus.UNPAID["value"])
    message = SupportBotMessage.DECLINE_PAYMENT_ORDER[lang].format(order_number=order.order_number)

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML",
    )

    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=telegram.InlineKeyboardMarkup([]),
        parse_mode="HTML",
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    bot = Bot(token=shop_telegram_bot.telegram_bot.bot_token)
    text = helpers.load_message(lang, "lead_order", order=order,
                                order_status=OrderStatus.items[order.status][lang], amount=amount)

    await bot.send_message(chat_id=order.lead.chat_id, text=text)


async def prepare_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.PREPARATION["value"])
    message = SupportBotMessage.PREPARE_ORDER[lang].format(order_number=order.order_number)

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML",
    )
    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=get_prepare_order_reply_markup(order, lang),
        parse_mode="HTML",
    )
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    bot = Bot(token=shop_telegram_bot.telegram_bot.bot_token)
    text = helpers.load_message(lang, "lead_order", order=order,
                                order_status=OrderStatus.items[order.status][lang], amount=amount)

    await bot.send_message(chat_id=order.lead.chat_id, text=text)


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


async def send_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
        return

    order = services.shop.order.change_status(db, order=order, status=OrderStatus.SENT["value"])
    message = SupportBotMessage.SEND_ORDER[lang].format(order_number=order.order_number)

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id,
        parse_mode="HTML",
    )
    await update.message.edit_text(
        text=get_order_message(order, lang, amount),
        reply_markup=telegram.InlineKeyboardMarkup([]),
        parse_mode="HTML",
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    bot = Bot(token=shop_telegram_bot.telegram_bot.bot_token)
    text = helpers.load_message(lang, "lead_order", order=order,
                                order_status=OrderStatus.items[order.status][lang], amount=amount)

    await bot.send_message(chat_id=order.lead.chat_id, text=text)


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
    for item in order.items:
        amount += item.count * item.price

    text = helpers.load_message(
        lang, "order",
        amount=amount,
        order=order,
        lead_number=lead.lead_number,
        order_status=OrderStatus.items[order.status]["title"][lang]
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
    res: telegram.Message = await shop_bot.send_message(chat_id=lead.chat_id, text=text)

    await bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text=SupportBotMessage.DIRECT_MESSAGE_SEND_SUCCESSFULLY[lang])

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
    text = helpers.load_message(
        lang, "order",
        amount=amount,
        order=order,
        order_status=OrderStatus.items[order.status]["title"][lang],
        lead_number=order.lead.lead_number,
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
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}")  # noqa
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
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}"),  # noqa
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_unpaid_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_ORDER['command']}:{order.uuid}"
            ),  # noqa
        ],
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}"  # noqa
            ),
        ],
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
        ],
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}"  # noqa
            ),
        ],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_send_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_DIRECT_MESSAGE["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_DIRECT_MESSAGE['command']}:{order.lead_id}"  # noqa
            ),  # noqa
        ],
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
        ],
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

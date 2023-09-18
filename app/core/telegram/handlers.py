import telegram
from jinja2 import Environment, FileSystemLoader
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.order_status import OrderStatus
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.constants.telegram_support_bot_commands import \
    TelegramSupportBotCommand
from app.core.config import settings
from app.core.telegram.messages import SupportBotMessage


async def telegram_support_bot_handler(db: Session, data: dict, lang: str):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    if data.get("callback_query"):
        update = telegram.Update.de_json(
            {"update_id": data["update_id"], **data["callback_query"]}, bot
        )
        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")
        if command == TelegramCallbackCommand.ACCEPT_ORDER["command"]:
            await accept_order_handler(db, update, arg, lang)

        if command == TelegramCallbackCommand.DECLINE_ORDER["command"]:
            await decline_order_handler(db, update, arg, lang)

        if command == TelegramCallbackCommand.DECLINE_PAYMENT_ORDER["command"]:
            await decline_payment_order_handler(db, update, arg, lang)

        if command == TelegramCallbackCommand.PREPARE_ORDER["command"]:
            await prepare_order_handler(db, update, arg, lang)

        if command == TelegramCallbackCommand.SEND_ORDER["command"]:
            await send_order_handler(db, update, arg, lang)

        if command == TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT["command"]:
            await verify_support_account(db, update, arg, lang)

    else:
        update: telegram.Update = telegram.Update.de_json(data, bot=bot)
        if update.message.text == TelegramSupportBotCommand.START["command"]:
            await update.message.reply_text(SupportBotMessage.ENTER_CODE[lang])

        elif update.message.text == TelegramSupportBotCommand.PAYMENT_CHECK_ORDERS["command"]:
            chat_id = update.message.chat_id
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=chat_id)

            if not shop_telegram_bot:
                await update.message.reply_text(
                    SupportBotMessage.ACCOUNT_NOT_REGISTER[lang]
                )
                return

            orders = services.shop.order.get_shop_orders(db, shop_id=shop_telegram_bot.shop_id, status=[OrderStatus.PAYMENT_CHECK["value"]])  # noqa

            for order in orders:
                text = get_payment_check_order_message(order, lang)
                reply_markup = get_payment_check_order_reply_markup(order, lang)
                await update.message.reply_text(
                    text, reply_markup=reply_markup
                )
            return
        elif update.message.text == TelegramSupportBotCommand.ACCEPTED_ORDERS["command"]:
            chat_id = update.message.chat_id
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=chat_id)

            if not shop_telegram_bot:
                await update.message.reply_text(
                    SupportBotMessage.ACCOUNT_NOT_REGISTER[lang]
                )
                return

            orders = services.shop.order.get_shop_orders(db, shop_id=shop_telegram_bot.shop_id, status=[OrderStatus.ACCEPTED["value"]])  # noqa

            for order in orders:
                text = get_accepted_order_message(order, lang)
                reply_markup = get_accepted_order_reply_markup(order, lang)

                await update.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                )
        elif update.message.text == TelegramSupportBotCommand.UNPAID_ORDERS["command"]:
            chat_id = update.message.chat_id
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=chat_id)

            if not shop_telegram_bot:
                await update.message.reply_text(
                    SupportBotMessage.ACCOUNT_NOT_REGISTER[lang]
                )
                return

            orders = services.shop.order.get_shop_orders(
                db, shop_id=shop_telegram_bot.shop_id, status=[OrderStatus.UNPAID["value"]])  # noqa

            for order in orders:
                text = get_unpaid_order_message(order, lang)
                reply_markup = get_unpaid_order_reply_markup(order, lang)

                await update.message.reply_text(
                    text, reply_markup=reply_markup
                )
        elif update.message.text.isnumeric():
            order_number = int(update.message.text)
            await send_order(db, update, order_number, lang)
        else:

            code = update.message.text.lstrip().rstrip()
            if len(code) != 8:
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
                db, support_token=code)
            if not shop_telegram_bot:
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return
            if shop_telegram_bot.is_support_verified:
                await update.message.reply_text(
                    SupportBotMessage.SHOP_ALREADY_CONNECTED[lang].format(
                        title=shop_telegram_bot.shop.title)
                )
                return
            text, reply_markup = verify_shop_support_account_message(shop_telegram_bot, lang)
            await update.message.reply_text(
                text, reply_markup=reply_markup
            )
            services.shop.shop_telegram_bot.set_support_account_chat_id(
                db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)
            return


def load_message(lang, template_name, **kwargs) -> str:
    file_path = f'app/templates/telegram/{lang}'
    file_loader = FileSystemLoader(file_path)
    env = Environment(loader=file_loader)
    template = env.get_template(f"{template_name}.txt")
    return template.render(**kwargs)


async def send_lead_pay_notification_to_support_bot_handler(db: Session, order_id: int, lang: str):
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    if not shop_telegram_bot:
        return

    message = SupportBotMessage.PAY_ORDER_NOTIFICATION[lang].format(
        order_number=order.order_number)

    bot = Bot(settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(chat_id=shop_telegram_bot.support_account_chat_id, text=message)


async def send_order(db: Session, update: telegram.Update, order_number: int, lang: str):

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
        db, chat_id=update.message.chat_id)

    if not shop_telegram_bot:
        return

    order = services.shop.order.get_by_order_number_and_shop_id(
        db, order_number=order_number, shop_id=shop_telegram_bot.shop_id)

    if not order:
        await update.message.reply_text(
            SupportBotMessage.ORDER_NOT_FOUND["fa"].format(order_number=order_number)
        )
        return

    amount = 0
    for item in order.items:
        amount += item.price * item.count

    reply_markup = telegram.InlineKeyboardMarkup([])
    text = ""

    if order.status == OrderStatus.PAYMENT_CHECK["value"]:
        reply_markup = get_payment_check_order_reply_markup(order, lang)
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.PAYMENT_CHECK["title"][lang])

    elif order.status == OrderStatus.ACCEPTED["value"]:
        reply_markup = get_accepted_order_reply_markup(order, lang)
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.ACCEPTED["title"][lang])

    elif order.status == OrderStatus.PREPARATION["value"]:
        reply_markup = get_prepare_order_reply_markup(order, lang)
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.PREPARATION["title"][lang])

    elif order.status == OrderStatus.UNPAID["value"]:
        reply_markup = get_unpaid_order_reply_markup(order, lang)
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.UNPAID["title"][lang])

    elif order.status == OrderStatus.DECLINED["value"]:
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.DECLINED["title"][lang])

    elif order.status == OrderStatus.SENT["value"]:
        text = load_message(lang, "order", amount=amount, order=order,
                            order_status=OrderStatus.SENT["title"][lang])
        reply_markup = telegram.InlineKeyboardMarkup([])

    await update.message.reply_text(text=text, reply_markup=reply_markup)


async def verify_support_account(db: Session, update: telegram.Update,
                                 shop_telegram_bot_uuid: UUID4, lang: str):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_uuid(
        db, uuid=shop_telegram_bot_uuid)
    if not shop_telegram_bot_uuid:
        await update.message.reply_text(text=SupportBotMessage.ACCOUNT_NOT_REGISTER[lang])

    services.shop.shop_telegram_bot.verify_support_account(db, db_obj=shop_telegram_bot)
    await update.message.reply_text(
        SupportBotMessage.ACCOUNT_CONNECTED_SUCCESSFULLY["fa"].format(
            title=shop_telegram_bot.shop.title
        )
    )
    await update.message.edit_reply_markup(reply_markup=telegram.InlineKeyboardMarkup([]))


def verify_shop_support_account_message(shop_telegram_bot: models.shop.ShopShopTelegramBot,
                                        lang: str):
    text = SupportBotMessage.ACCEPT_SHOP[lang].format(title=shop_telegram_bot.shop.title)
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

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.ACCEPTED["value"])

    message = SupportBotMessage.ACCEPT_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id
    )
    await update.message.edit_text(
        text=get_accepted_order_message(order, lang),
        reply_markup=get_accepted_order_reply_markup(order, lang)
    )


async def decline_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.DECLINED["value"])

    message = SupportBotMessage.DECLINE_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id
    )
    await update.message.edit_reply_markup(telegram.InlineKeyboardMarkup([]))
    await update.message.edit_text(text=get_declined_order_message(order, lang))


async def decline_payment_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    order = services.shop.order.change_status(db, order=order, status=OrderStatus.UNPAID["value"])
    message = SupportBotMessage.DECLINE_PAYMENT_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id
    )

    await update.message.edit_text(
        text=get_unpaid_order_message(order, lang),
        reply_markup=telegram.InlineKeyboardMarkup([])
    )


async def prepare_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.PREPARATION["value"])
    message = SupportBotMessage.PREPARE_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id
    )
    await update.message.edit_text(
        text=get_prepare_order_message(order, lang),
        reply_markup=get_prepare_order_reply_markup(order, lang)
    )


async def send_order_handler(db: Session, update: telegram.Update, order_id, lang):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return

    order = services.shop.order.change_status(db, order=order, status=OrderStatus.SENT["value"])
    message = SupportBotMessage.SEND_ORDER[lang].format(order_number=order.order_number)

    await update.message.reply_text(
        message,
        reply_to_message_id=update.message.message_id
    )
    await update.message.edit_text(
        text=get_send_order_message(order, lang),
        reply_markup=telegram.InlineKeyboardMarkup([])
    )


async def telegram_bot_webhook_handler(db: Session, data: dict, bot_id: int):
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)

    if not shop_telegram_bot:
        return

    user = data["message"]["from"]
    lead = services.social.telegram_lead.get_by_chat_id(db, chat_id=user.get("id"))
    if not lead:
        services.social.telegram_lead.create(
            db,
            obj_in=schemas.social.TelegramLeadCreate(
                telegram_bot_id=shop_telegram_bot.telegram_bot_id,
                chat_id=user.get("id"),
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                username=user.get("username"),
            )
        )
    bot = Bot(token=telegram_bot.bot_token)
    update = telegram.Update.de_json(data, bot)

    await update.message.reply_text(
        text=f"Hi, you are using `{shop_telegram_bot.shop.title}` shop",
        reply_markup=get_shop_menu(telegram_bot.uuid, shop_telegram_bot.shop.uuid)
    )


async def send_lead_order_to_bot_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):

    telegram_bot = services.telegram_bot.get(db, id=telegram_bot_id)
    if not telegram_bot:
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

    amount = 0
    for item in order.items:
        amount += item.count * item.price

    text = load_message(lang, "new_order", amount=amount, order=order)

    bot = Bot(token=telegram_bot.bot_token)
    await bot.send_message(chat_id=lead.chat_id, text=text)
    return


async def send_lead_order_to_shop_support_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int, lang):

    lead = services.social.telegram_lead.get(db, id=lead_id)
    if not lead:
        return
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead.id != order.lead_id:
        return

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot_id)
    if not shop_telegram_bot:
        return

    if lead.telegram_bot_id != shop_telegram_bot.telegram_bot_id:
        return
    amount = 0
    for item in order.items:
        amount += item.count * item.price

    text = load_message(lang, "new_order", amount=amount, order=order)
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(chat_id=shop_telegram_bot.support_account_chat_id, text=text)
    return


def get_shop_menu(bot_id: UUID4, lead_id: UUID4):
    keyboard = [
        [
            telegram.MenuButtonWebApp(
                text="View Shop",
                web_app=telegram.WebAppInfo(f"{settings.PLATFO_SHOPS_BASE_URL}/{bot_id}/{lead_id}")
            )
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup


def get_payment_check_order_message(order: models.shop.ShopOrder, lang):
    total_price = 0
    for item in order.items:
        total_price += item.price * item.count

    text = load_message(
        lang, "payment_check",
        amount=total_price,
        order=order,
        status=OrderStatus.PAYMENT_CHECK["title"][lang],
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
                callback_data=f"{TelegramCallbackCommand.DECLINE_PAYMENT_ORDER['command']}:{order.uuid}")
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_accepted_order_message(order: models.shop.ShopOrder, lang):
    amount = 0
    for item in order.items:
        amount += item.price * item.count
    text = load_message(
        lang, "accepted_order",
        amount=amount,
        order=order,
        status=OrderStatus.ACCEPTED["title"][lang],
    )

    return text


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
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_declined_order_message(order: models.shop.ShopOrder, lang):
    amount = 0
    for item in order.items:
        amount += item.price * item.count
    text = load_message(
        lang,
        "declined_order",
        amount=amount,
        order=order,
        status=OrderStatus.DECLINED["title"][lang],
    )

    return text


def get_unpaid_order_message(order: models.shop.ShopOrder, lang):
    amount = 0
    for item in order.items:
        amount += item.price * item.count
    text = load_message(
        lang,
        "unpaid_order",
        amount=amount,
        order=order,
        order_status=OrderStatus.UNPAID["title"][lang]
    )

    return text


def get_unpaid_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.ACCEPT_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.ACCEPT_ORDER['command']}:{order.uuid}"
            ),  # noqa
        ],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_prepare_order_message(order: models.shop.ShopOrder, lang):
    total_price = 0
    for item in order.items:
        total_price += item.price * item.count

    text = load_message(
        lang, "order",
        amount=total_price,
        order=order,
        order_status=OrderStatus.PREPARATION["title"][lang]
    )

    return text


def get_prepare_order_reply_markup(order: models.shop.ShopOrder, lang):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.SEND_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.SEND_ORDER['command']}:{order.uuid}"
            ),  # noqa
        ],
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_send_order_message(order: models.shop.ShopOrder, lang):
    total_price = 0
    for item in order.items:
        total_price += item.price * item.count

    text = load_message(
        lang, "order",
        amount=total_price,
        order=order,
        order_status=OrderStatus.SENT["title"][lang]
    )
    return text

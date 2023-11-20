import telegram

from app import models
from app.constants.telegram_callback_command import TelegramCallbackCommand


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


def get_empty_reply_markup(*args, **kwargs):
    return telegram.InlineKeyboardMarkup([])


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


def get_pay_order_reply_markup(order_id, lang: str):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                TelegramCallbackCommand.PAY_ORDER["title"][lang],
                callback_data=f"{TelegramCallbackCommand.PAY_ORDER['command']}:{order_id}")  # noqa
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return reply_markup

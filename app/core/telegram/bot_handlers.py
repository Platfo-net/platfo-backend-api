import os

import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, services
from app.constants.currency import Currency
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.constants.telegram_bot_command import TelegramBotCommand
from app.core import security
from app.core.config import settings
from app.core.telegram import helpers, support_bot_handlers
from app.core.telegram.messages import SupportBotMessage

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
            "price": helpers.number_to_price(int(item.price)),
            "title": item.product.title,
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


async def handle_order_payment(
    db: Session,
    data: dict,
    telegram_order: models.shop.ShopTelegramOrder,
    shop_telegram_bot: models.shop.ShopShopTelegramBot,
    bot: telegram.Bot,
    lang: str
):
    support_bot = Bot(settings.SUPPORT_BOT_TOKEN)

    update = telegram.Message.de_json(data["message"], bot)
    if update.photo:
        photo_unique_id = update.photo[-1].file_id
        url, file_name = await helpers.download_and_upload_telegram_image(
            bot, photo_unique_id, settings.S3_TELEGRAM_BOT_IMAGES_BUCKET)
        if not url:
            await update.reply_text(text="Error in processing image")

        order = services.shop.order.get(db, id=telegram_order.order_id)
        order = services.shop.order.change_status(
            db, order=order, status=OrderStatus.PAYMENT_CHECK["value"])
        services.shop.order.add_payment_image(db, db_obj=order, image_name=file_name)

        image_caption = helpers.load_message(
            lang,
            "payment_image_caption",
            order_number=order.order_number,
            lead_number=order.lead.lead_number
        )
        print(url)
        await support_bot.send_photo(
            caption=image_caption,
            photo=url,
            reply_to_message_id=telegram_order.support_bot_message_id,
            chat_id=shop_telegram_bot.support_account_chat_id)

        os.remove(file_name)

    else:
        order = services.shop.order.get(db, id=telegram_order.order_id)
        order = services.shop.order.change_status(
            db, order=order, status=OrderStatus.PAYMENT_CHECK["value"])
        services.shop.order.add_payment_information(db, db_obj=order, information=update.text)

        text = helpers.load_message(
            lang,
            "payment_image_caption",
            order_number=order.order_number,
            lead_number=order.lead.lead_number,
            text=update.text,
        )

        await support_bot.send_message(
            text=text,
            reply_to_message_id=telegram_order.support_bot_message_id,
            chat_id=shop_telegram_bot.support_account_chat_id,
        )

    await update.reply_text(
        text=SupportBotMessage.PAYMENT_INFORMATION_SENT[lang],
    )

    amount = 0
    for item in order.items:
        amount += item.count * item.price
    await support_bot.edit_message_text(
        text=support_bot_handlers.get_order_message(order, lang, amount),
        chat_id=shop_telegram_bot.support_account_chat_id,
        message_id=telegram_order.support_bot_message_id,
        reply_markup=support_bot_handlers.get_payment_check_order_reply_markup(
            order, lang),
        parse_mode="HTML"
    )


async def set_all_bot_commands_task_handler(db: Session, lang):
    telegram_bots = services.telegram_bot.all(db)
    for telegram_bot in telegram_bots:
        bot = Bot(security.decrypt_telegram_token(telegram_bot.bot_token))
        await bot.set_my_commands(
            commands=[
                telegram.BotCommand(
                    command["command"],
                    command["description"],
                ) for command in TelegramBotCommand.commands
            ]
        )

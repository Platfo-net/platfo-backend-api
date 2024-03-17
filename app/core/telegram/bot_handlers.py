import os

import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, services
from app.constants.currency import Currency
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.constants.telegram_bot_command import TelegramBotCommand
from app.core import security
from app.core.config import settings
from app.core.telegram import helpers
from app.core.telegram.messages import SupportBotMessage


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
    # if not lead:
    #     return
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if lead and lead.id != order.lead_id:
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
    amount += order.shipment_cost_amount
    currency = Currency.IRT["name"]

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
    reply_markup = None
    if order.shop_payment_method.payment_method.title == PaymentMethod.CARD_TRANSFER["title"]:
        reply_markup = helpers.get_pay_order_reply_markup(
            order_id, lang)

    order_message: telegram.Message = await bot.send_message(
        chat_id=lead.chat_id, text=text, reply_markup=reply_markup, parse_mode="HTML")

    return order_message.message_id


async def send_lead_pay_message(
        db: Session, telegram_bot: models.TelegramBot,
        lead: models.social.TelegramLead, order_id: int, lang):

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)

    if not helpers.has_credit_by_shop_id(db, shop_id=shop_telegram_bot.shop_id):
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
    amount += order.shipment_cost_amount

    currency = Currency.IRT["name"]

    shop_payment_method = services.shop.shop_payment_method.get(
        db, id=order.shop_payment_method_id
    )
    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))

    if order.shop_payment_method.payment_method.title == PaymentMethod.CARD_TRANSFER["title"]:

        text = helpers.load_message(
            lang,
            "card_transfer_payment_notification",
            amount=helpers.number_to_price(int(amount)),
            currency=currency,
            card_number=shop_payment_method.information["card_number"],
            name=shop_payment_method.information["name"],
            bank=shop_payment_method.information.get("bank", "")
        )
        telegram_order = services.shop.telegram_order.get_by_order_id(
            db, order_id=order.id)

        payment_info_message: telegram.Message = await bot.send_message(
            chat_id=lead.chat_id, text=text, parse_mode="HTML")
        services.shop.telegram_order.add_reply_to_message_info(
            db, telegram_order_id=telegram_order.id,
            message_reply_to_id=payment_info_message.message_id
        )
        return


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
        services.shop.order.add_payment_image(
            db, db_obj=order, image_name=file_name)

        image_caption = helpers.load_message(
            lang,
            "payment_image_caption",
            order_number=order.order_number,
            lead_number=order.lead.lead_number
        )
        await support_bot.send_photo(
            caption=image_caption,
            photo=url,
            reply_to_message_id=telegram_order.support_bot_message_id,
            chat_id=shop_telegram_bot.support_account_chat_id)

        os.remove(file_name)

    elif update.text:
        order = services.shop.order.get(db, id=telegram_order.order_id)
        order = services.shop.order.change_status(
            db, order=order, status=OrderStatus.PAYMENT_CHECK["value"])
        services.shop.order.add_payment_information(
            db, db_obj=order, information=update.text)

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
    else:
        await update.reply_text(text=SupportBotMessage.INVALID_INPUT[lang])
        return

    await update.reply_text(
        text=SupportBotMessage.PAYMENT_INFORMATION_SENT[lang],
    )

    amount = 0
    for item in order.items:
        amount += item.count * item.price
    amount += order.shipment_cost_amount

    await support_bot.edit_message_text(
        text=helpers.get_order_message(order, lang, amount),
        chat_id=shop_telegram_bot.support_account_chat_id,
        message_id=telegram_order.support_bot_message_id,
        reply_markup=helpers.get_payment_check_order_reply_markup(
            order, lang),
        parse_mode="HTML"
    )


async def send_lead_pay_notification_to_bot_handler(db: Session, order_id: int, lang: str):
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)
    if not shop_telegram_bot:
        return
    bot = telegram.Bot(security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    await bot.send_message(
        text=f"پرداخت سفارش شما با موفقیت انجام شد {order.payment_information.get('ref_id')}",
        chat_id=order.lead.chat_id
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


async def order_change_status_from_dashboard_handler(
    db: Session,
    order_id: int,
    lang: str,
):
    order = services.shop.order.get(db, id=order_id)
    if not order:
        return

    if not helpers.has_credit_by_shop_id(db, order.shop_id):
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
        pass

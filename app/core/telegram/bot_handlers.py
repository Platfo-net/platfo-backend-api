import os
from typing import Optional

import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.currency import Currency
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.constants.telegram_bot_command import TelegramBotCommand
from app.core import security, storage
from app.core.config import settings
from app.core.telegram import helpers
from app.core.telegram.messages import SupportBotMessage
from app.llms.repository.chatbot_repository import ChatBotRepository
from app.llms.repository.knowledge_base_repository import KnowledgeBaseRepository
from app.llms.services.chatbot_service import ChatBotService
from app.llms.services.knowledge_base_service import KnowledgeBaseService
from app.llms.utils.langchain.pipeline import get_question_and_answer, \
    get_question_and_answer_multi_vector


async def send_lead_order_to_bot_handler(db: Session, telegram_bot_id: int, lead_id: int,
                                         order_id: int, lang):

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
            "title": item.product_title,
            "count": item.count,
            "variant_title": item.variant_title,
        })
    amount += order.shipment_cost_amount
    currency = Currency.IRT["name"]

    text = helpers.load_message(
        lang, "lead_new_order", amount=helpers.number_to_price(int(amount)), order=order,
        items=items, order_status=OrderStatus.items[order.status]["title"][lang],
        payment_method=PaymentMethod.items[order.shop_payment_method.payment_method.title][lang],
        currency=currency,
        shipment_cost_amount=helpers.number_to_price(int(order.shipment_cost_amount)))
    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))

    order_message: telegram.Message = await bot.send_message(chat_id=lead.chat_id, text=text,
                                                             parse_mode="HTML")

    return order_message.message_id


async def send_lead_pay_message(db: Session, telegram_bot: models.TelegramBot,
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
            "title": item.product_title,
            "count": item.count,
            "variant_title": item.variant_title,
        })
    amount += order.shipment_cost_amount

    currency = Currency.IRT["name"]

    shop_payment_method = services.shop.shop_payment_method.get(db,
                                                                id=order.shop_payment_method_id)
    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))

    if order.shop_payment_method.payment_method.title == PaymentMethod.CARD_TRANSFER["title"]:

        text = helpers.load_message(lang, "card_transfer_payment_notification",
                                    amount=helpers.number_to_price(int(amount)), currency=currency,
                                    card_number=shop_payment_method.information["card_number"],
                                    name=shop_payment_method.information["name"],
                                    bank=shop_payment_method.information.get("bank", ""))
        telegram_order = services.shop.telegram_order.get_by_order_id(db, order_id=order.id)

        payment_info_message: telegram.Message = await bot.send_message(
            chat_id=lead.chat_id, text=text, parse_mode="HTML")
        services.shop.telegram_order.add_reply_to_message_info(
            db, telegram_order_id=telegram_order.id,
            message_reply_to_id=payment_info_message.message_id)
        return


async def handle_order_payment(db: Session, update: telegram.Update,
                               telegram_order: models.shop.ShopTelegramOrder,
                               shop_telegram_bot: models.shop.ShopShopTelegramBot,
                               bot: telegram.Bot, lang: str):
    support_bot = Bot(settings.SUPPORT_BOT_TOKEN)

    if update.message.photo:
        photo_unique_id = update.photo[-1].file_id
        url, file_name = await helpers.download_and_upload_telegram_image(
            bot, photo_unique_id, settings.S3_TELEGRAM_BOT_IMAGES_BUCKET)
        if not url:
            await update.message.reply_text(text="Error in processing image")

        order = services.shop.order.get(db, id=telegram_order.order_id)
        order = services.shop.order.change_status(db, order=order,
                                                  status=OrderStatus.PAYMENT_CHECK["value"])
        services.shop.order.add_payment_image(db, db_obj=order, image_name=file_name)

        image_caption = helpers.load_message(lang, "payment_image_caption",
                                             order_number=order.order_number,
                                             lead_number=order.lead.lead_number)
        await support_bot.send_photo(caption=image_caption, photo=url,
                                     reply_to_message_id=telegram_order.support_bot_message_id,
                                     chat_id=shop_telegram_bot.support_account_chat_id)

        os.remove(file_name)

    elif update.message.text:
        order = services.shop.order.get(db, id=telegram_order.order_id)
        order = services.shop.order.change_status(db, order=order,
                                                  status=OrderStatus.PAYMENT_CHECK["value"])
        services.shop.order.add_payment_information(db, db_obj=order, information=update.text)

        text = helpers.load_message(
            lang,
            "payment_image_caption",
            order_number=order.order_number,
            lead_number=order.lead.lead_number,
            text=update.message.text,
        )

        await support_bot.send_message(
            text=text,
            reply_to_message_id=telegram_order.support_bot_message_id,
            chat_id=shop_telegram_bot.support_account_chat_id,
        )
    else:
        await update.message.reply_text(text=SupportBotMessage.INVALID_INPUT[lang])
        return

    await update.message.reply_text(
        text=SupportBotMessage.PAYMENT_INFORMATION_SENT[lang],
    )

    amount = 0
    for item in order.items:
        amount += item.count * item.price
    amount += order.shipment_cost_amount

    await support_bot.edit_message_text(
        text=helpers.get_order_message(order, lang,
                                       amount), chat_id=shop_telegram_bot.support_account_chat_id,
        message_id=telegram_order.support_bot_message_id,
        reply_markup=helpers.get_payment_check_order_reply_markup(order, lang), parse_mode="HTML")


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
        chat_id=order.lead.chat_id)


async def set_all_bot_commands_task_handler(db: Session, lang):
    telegram_bots = services.telegram_bot.all(db)
    for telegram_bot in telegram_bots:
        bot = Bot(security.decrypt_telegram_token(telegram_bot.bot_token))
        await bot.set_my_commands(commands=[
            telegram.BotCommand(
                command["command"],
                command["description"],
            ) for command in TelegramBotCommand.commands
        ])


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
            "title": item.product_title,
            "count": item.count,
            "variant_title": item.variant_title,
        })
    amount += order.shipment_cost_amount

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=order.shop_id)

    bot = Bot(token=security.decrypt_telegram_token(shop_telegram_bot.telegram_bot.bot_token))
    text = helpers.load_message(lang, "order_change_status_notification",
                                order_status=OrderStatus.items[order.status]["title"][lang],
                                order_number=order.order_number)
    try:
        await bot.send_message(chat_id=order.lead.chat_id, text=text)
    except telegram.error.Forbidden:
        pass


async def handle_start_message(telegram_bot: models.TelegramBot, update: telegram.Update,
                               lang) -> telegram.Message:

    if update.message:
        message = update.message
    else:
        message = update.effective_message

    if telegram_bot.welcome_message:
        text = helpers.load_message(lang, "bot_overview",
                                    welcome_message=telegram_bot.welcome_message)
        button_name = telegram_bot.button_name
        app_link = telegram_bot.app_link
        image_url = storage.get_object_url(telegram_bot.image,
                                           settings.S3_TELEGRAM_BOT_MENU_IMAGES_BUCKET)
        if image_url:
            sent_message = await message.reply_photo(
                caption=text, photo=image_url,
                reply_markup=helpers.get_bot_menu(button_name, app_link), parse_mode="HTML")
        else:
            sent_message = await message.reply_text(
                text=text, reply_markup=helpers.get_bot_menu(button_name, app_link),
                parse_mode="HTML")
    else:
        text = helpers.load_message(lang, "default_message")
        app_link = "https://platfo.net"
        button_name = "پلتفو"
        sent_message = await message.reply_text(
            text=text, reply_markup=helpers.get_bot_menu(button_name, app_link), parse_mode="HTML")

    return sent_message


async def handle_chatbot_qa_answering(db: Session, message: telegram.Message, chatbot_id: int):

    chatbot_service = ChatBotService(ChatBotRepository(db))
    knowledge_base_service = KnowledgeBaseService(KnowledgeBaseRepository(db))
    answer, knowledge_bases = get_question_and_answer_multi_vector(message.text, chatbot_id,
                                                                   chatbot_service,
                                                                   knowledge_base_service)

    if knowledge_bases:
        try:
            button_name = knowledge_bases[0].name
            source_link = knowledge_bases[0].source_link

            keyboard = [[
                telegram.MenuButtonWebApp(text=button_name,
                                          web_app=telegram.WebAppInfo(source_link))
            ]]

            reply_markup = telegram.InlineKeyboardMarkup(keyboard)

            sent_message = await message.reply_text(text=answer, reply_markup=reply_markup)
            return sent_message
        except Exception:
            pass
    sent_message = await message.reply_text(answer)
    return sent_message


def get_message(update: telegram.Update):
    if update.message:
        return update.message
    elif update.effective_message:
        return update.effective_message
    return


async def handle_chatbot_qa(db: Session, update: telegram.Update, chatbot_id: int,
                            telegram_bot) -> telegram.Message:
    message = get_message(update)

    return await handle_chatbot_qa_answering(db, message, chatbot_id)


def get_update(data: dict, bot) -> telegram.Update:
    if data.get("callback_query"):
        update = telegram.Update.de_json({
            "update_id": data["update_id"],
            **data["callback_query"]
        }, bot)
    else:
        update = telegram.Update.de_json(data, bot)

    return update


def save_lead_message(
    db: Session,
    update: telegram.Update,
    lead: models.social.TelegramLead,
    mirror_message: telegram.Message,
) -> Optional[models.social.TelegramLeadMessage]:
    message = get_message(update)
    if not message:
        return

    db_message = services.social.telegram_lead_message.create(
        db, obj_in=schemas.social.TelegramLeadMessageCreate(
            lead_id=lead.id,
            is_lead_to_bot=True,
            message=message.text,
            message_id=message.message_id,
            mirror_message_id=None if not mirror_message else mirror_message.id,
            reply_to_id=None
            if not message.reply_to_message else message.reply_to_message.message_id,
        ))
    return db_message


def save_bot_message(
    db: Session,
    message: telegram.Message,
    lead: models.social.TelegramLead,
) -> Optional[models.social.TelegramLeadMessage]:
    db_message = services.social.telegram_lead_message.create(
        db, obj_in=schemas.social.TelegramLeadMessageCreate(
            lead_id=lead.id,
            is_lead_to_bot=False,
            message=message.text,
            message_id=message.message_id,
            mirror_message_id=None,
            reply_to_id=None
            if not message.reply_to_message else message.reply_to_message.message_id,
        ))
    return db_message


async def send_vitrin(update: telegram.Update, shop_uuid, lead_uuid, lang):
    return await update.message.reply_text(
        text="ویترین", reply_markup=helpers.get_shop_menu(shop_uuid, lead_uuid, lang),
        parse_mode="HTML")


async def handle_shop_message(db: Session, telegram_bot_id, update: telegram.Update,
                              lead: models.social.TelegramLead, lang):
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot_id)
    if not shop_telegram_bot:
        return None, None
    bot = update.get_bot()
    if update.message.text == TelegramBotCommand.VITRIN["command"]:
        return await send_vitrin(update, shop_telegram_bot.shop.uuid, lead.uuid, lang), None

    elif update.message.text == TelegramBotCommand.SEND_DIRECT_MESSAGE["command"]:
        text = helpers.load_message(lang, "lead_to_support_message_helper",
                                    lead_number=lead.lead_number)
        return await update.message.reply_text(text=text, parse_mode="HTML"), None

    else:
        message = update.message.text
        text = helpers.load_message(lang, "lead_to_support_message", lead_number=lead.lead_number,
                                    message=message)
        mirror_message = await bot.send_message(chat_id=shop_telegram_bot.support_account_chat_id,
                                                text=text, parse_mode="HTML")
        return None, mirror_message

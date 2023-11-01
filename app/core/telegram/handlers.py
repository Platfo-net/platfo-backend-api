import os
from uuid import uuid4

import requests
import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.currency import Currency
from app.constants.module import Module
from app.constants.order_status import OrderStatus
from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.constants.telegram_bot_command import TelegramBotCommand
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.constants.telegram_support_bot_commands import \
    TelegramSupportBotCommand
from app.core import security, storage
from app.core.config import settings
from app.core.telegram import bot_handlers, helpers, support_bot_handlers
from app.core.telegram.messages import SupportBotMessage


async def telegram_support_bot_handler(db: Session, data: dict, lang: str):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    if data.get("callback_query"):
        update = telegram.Update.de_json(
            {"update_id": data["update_id"], **data["callback_query"]}, bot
        )

        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")
        if command == TelegramCallbackCommand.NEW_CONNECTION.get("command"):
            text = helpers.load_message(lang, "new_connection")
            await update.message.reply_text(text, parse_mode="HTML")
            return
        if command == TelegramCallbackCommand.CREDIT_PLAN.get("command"):
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            await support_bot_handlers.handle_credit_plan(db, update, arg, lang, shop_telegram_bot.shop_id)
            return
        elif command == TelegramCallbackCommand.ACCEPT_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db, update, arg, lang,
                OrderStatus.ACCEPTED,
                SupportBotMessage.ACCEPT_ORDER,
                support_bot_handlers.get_accepted_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.DECLINE_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db, update, arg, lang,
                OrderStatus.DECLINED,
                SupportBotMessage.DECLINE_ORDER,
                support_bot_handlers.get_declined_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.DECLINE_PAYMENT_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db, update, arg, lang,
                OrderStatus.PAYMENT_DECLINED,
                SupportBotMessage.DECLINE_PAYMENT_ORDER,
                support_bot_handlers.get_empty_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.PREPARE_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db, update, arg, lang,
                OrderStatus.PREPARATION,
                SupportBotMessage.PREPARE_ORDER,
                support_bot_handlers.get_prepare_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.SEND_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db, update, arg, lang,
                OrderStatus.SENT,
                SupportBotMessage.SEND_ORDER,
                support_bot_handlers.get_empty_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT.get("command"):
            await support_bot_handlers.verify_support_account(db, update, arg, lang)
            return
        elif command == TelegramCallbackCommand.SEND_DIRECT_MESSAGE.get("command"):
            await support_bot_handlers.send_direct_message_helper(db, update, arg, lang)
            return

    else:

        message = telegram.Message.de_json(data["message"], bot)
        if message.photo:
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=message.chat_id)
            await support_bot_handlers.handle_shop_credit_extending(
                db, message,
                settings.S3_SHOP_TELEGRAM_CREDIT_EXTENDING,
                shop_telegram_bot.shop_id,
                lang
            )
            return

        update: telegram.Update = telegram.Update.de_json(data, bot=bot)

        if update.message.text == TelegramSupportBotCommand.START["command"]:
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            if not shop_telegram_bot:
                text = support_bot_handlers.get_start_support_bot_message(lang)
                reply_markup = support_bot_handlers.get_start_support_bot_reply_markup(lang)
                await update.message.reply_text(
                    text=text, reply_markup=reply_markup, parse_mode="HTML")
                return
            else:
                text = helpers.load_message(
                    lang, "support_account_already_connected",
                    shop_title=shop_telegram_bot.shop.title)
                await update.message.reply_text(text=text, parse_mode="HTML")
                return

        elif update.message.text == TelegramSupportBotCommand.SEARCH_ORDER["command"]:
            await update.message.reply_text(
                SupportBotMessage.ENTER_ORDER_NUMBER[lang], parse_mode="HTML")
            return

        elif update.message.text == TelegramSupportBotCommand.CREDIT_EXTENDING["command"]:
            await support_bot_handlers.handle_credit_extending(db, update, lang)
            return

        elif update.message.text == TelegramSupportBotCommand.HELP_DIRECT_MESSAGE["command"]:
            message = helpers.load_message(lang, "direct_message_helper")
            await update.message.reply_text(message, parse_mode="HTML")
            message = helpers.load_message(lang, "direct_message_sample")
            await update.message.reply_text(message, parse_mode="HTML")

            return

        elif update.message.text == TelegramSupportBotCommand.PAYMENT_CHECK_ORDERS["command"]:
            await support_bot_handlers.send_all_order_by_status(
                db, update, OrderStatus.PAYMENT_CHECK,
                support_bot_handlers.get_order_message,
                support_bot_handlers.get_payment_check_order_reply_markup,
                lang,
            )
            return
        elif update.message.text == TelegramSupportBotCommand.ACCEPTED_ORDERS["command"]:
            await support_bot_handlers.send_all_order_by_status(
                db, update, OrderStatus.ACCEPTED,
                support_bot_handlers.get_order_message,
                support_bot_handlers.get_accepted_order_reply_markup,
                lang,
            )
            return

        elif update.message.text == TelegramSupportBotCommand.UNPAID_ORDERS["command"]:
            await support_bot_handlers.send_all_order_by_status(
                db, update, OrderStatus.UNPAID,
                support_bot_handlers.get_order_message,
                support_bot_handlers.get_unpaid_order_reply_markup,
                lang,
            )
            return
        elif update.message.text.startswith("/"):
            await update.message.reply_text(text=SupportBotMessage.INVALID_COMMAND[lang],
                                            parse_mode="HTML")
            return
        else:
            await support_bot_handlers.plain_message_handler(db, update, lang)
            return


async def telegram_bot_webhook_handler(db: Session, data: dict, bot_id: int, lang):
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)

    if not shop_telegram_bot:
        return

    user = data["message"]["from"]
    lead = services.social.telegram_lead.get_by_chat_id(
        db, chat_id=user.get("id"), telegram_bot_id=telegram_bot.id)
    if not lead:
        lead_number = services.social.telegram_lead.get_last_lead_number(
            db, telegram_bot_id=shop_telegram_bot.telegram_bot_id)
        lead = services.social.telegram_lead.create(
            db,
            obj_in=schemas.social.TelegramLeadCreate(
                telegram_bot_id=shop_telegram_bot.telegram_bot_id,
                chat_id=user.get("id"),
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                username=user.get("username"),
                lead_number=lead_number + 1,
            )
        )
    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))

    reply_to_message = data["message"].get("reply_to_message")
    if reply_to_message:
        telegram_order = services.shop.telegram_order.get_by_reply_to_id_and_lead_id(
            db, lead_id=lead.id, reply_to_id=reply_to_message["message_id"])
        if telegram_order:
            await bot_handlers.handle_order_payment(db, data, telegram_order, shop_telegram_bot, bot, lang)
            return

    update = telegram.Update.de_json(data, bot)
    if update.message.text == TelegramBotCommand.START["command"]:
        text = helpers.load_message(lang, "shop_overview", shop_title=shop_telegram_bot.shop.title)
        await update.message.reply_text(
            text=text,
            reply_markup=bot_handlers.get_shop_menu(shop_telegram_bot.shop.uuid, lead.uuid, lang),
            parse_mode="HTML"
        )

    elif update.message.text == TelegramBotCommand.SEND_DIRECT_MESSAGE["command"]:
        text = helpers.load_message(
            lang, "lead_to_support_message_helper", lead_number=lead.lead_number)
        await update.message.reply_text(
            text=text,
            parse_mode="HTML"
        )
    else:
        message = update.message.text
        bot = Bot(settings.SUPPORT_BOT_TOKEN)
        text = helpers.load_message(lang, "lead_to_support_message",
                                    lead_number=lead.lead_number, message=message)
        res: telegram.Message = await bot.send_message(
            chat_id=shop_telegram_bot.support_account_chat_id, text=text, parse_mode="HTML")
        reply_to_id = None
        if update.message.reply_to_message:
            reply_to_id = update.message.reply_to_message.message_id
        obj_in = schemas.social.TelegramLeadMessageCreate(
            lead_id=lead.id,
            is_lead_to_bot=True,
            message=message,
            message_id=update.message.message_id,
            mirror_message_id=res.message_id,
            reply_to_id=reply_to_id,
        )
        services.social.telegram_lead_message.create(db, obj_in=obj_in)
        return


async def telegram_admin_bot_handler(db: Session, data: dict, lang: str):
    bot = telegram.Bot(settings.TELEGRAM_ADMIN_BOT_TOKEN)
    update = telegram.Update.de_json(data, bot)

    await update.message.reply_text("helloooooo , wellcome to the hell")
    if data.get("callback_query"):
        update = telegram.Update.de_json(
            {"update_id": data["update_id"], **data["callback_query"]}, bot
        )


        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")

        if command == TelegramCallbackCommand.ACCEPT_CREDIT_EXTENDING.get("command"):
            await accept_credit_extending(db, update, int(arg), lang)
            return

        if command == TelegramCallbackCommand.ACCEPT_CREDIT_EXTENDING.get("command"):
            await decline_credit_extending(db, update, int(arg), lang)
            return


async def accept_credit_extending(db: Session, update: telegram.Update, shop_telegram_payment_record_id: int, lang):
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.get(
        db, id=shop_telegram_payment_record_id)
    credit = services.credit.shop_credit.get_by_shop_id(db, shop_telegram_payment_record.shop_id)

    services.credit.shop_credit.add_shop_credit(
        db, db_obj=credit, days=shop_telegram_payment_record.plan.extend_days
    )

    services.credit.shop_telegram_payment_record.change_status(
        db, db_obj=shop_telegram_payment_record, status=ShopTelegramPaymentRecordStatus.APPLIED)

    await update.message.reply_text("باشه", parse_mode="HTML")

    support_bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    await support_bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text="حساب شما شارژ شد",
        reply_to_message_id=shop_telegram_payment_record.payment_message_id,
    )


async def decline_credit_extending(
    db: Session,
    update: telegram.Update,
    shop_telegram_payment_record_id: int,
    lang
):
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.get(
        db, id=shop_telegram_payment_record_id)
    services.credit.shop_telegram_payment_record.change_status(
        db, db_obj=shop_telegram_payment_record, status=ShopTelegramPaymentRecordStatus.DECLINED)

    await update.message.reply_text("باشه", parse_mode="HTML")

    support_bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    await support_bot.send_message(
        chat_id=shop_telegram_bot.support_account_chat_id,
        text="حساب شما شارژ نشد",
        reply_to_message_id=shop_telegram_payment_record.payment_message_id,
    )

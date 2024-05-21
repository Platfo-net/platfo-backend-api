import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import schemas, services
from app.constants.message_builder import MessageBuilderButton, MessageBuilderCommand
from app.constants.order_status import OrderStatus
from app.constants.telegram_bot_command import TelegramBotCommand
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.constants.telegram_support_bot_commands import TelegramSupportBotCommand
from app.core import security
from app.core.config import settings
from app.core.telegram import bot_handlers, helpers, message_builder_bot, support_bot_handlers
from app.core.telegram.messages import SupportBotMessage
from app.llms.repository.chatbot_telegram_bot_repository import ChatBotTelegramBotRepository
from app.llms.services.chatbot_telegram_bot_service import ChatBotTelegramBotService


async def telegram_support_bot_handler(db: Session, data: dict, lang: str):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    if data.get("callback_query"):
        update = telegram.Update.de_json({
            "update_id": data["update_id"],
            **data["callback_query"]
        }, bot)

        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")
        if command == TelegramCallbackCommand.NEW_CONNECTION.get("command"):
            text = helpers.load_message(lang, "new_connection")
            await update.message.reply_text(text, parse_mode="HTML")
            return

        elif command == TelegramCallbackCommand.CREDIT_PLAN.get("command"):
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            await support_bot_handlers.handle_credit_plan(db, update, arg, lang,
                                                          shop_telegram_bot.shop_id)
            return

        elif command == TelegramCallbackCommand.ACCEPT_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db,
                update,
                arg,
                lang,
                OrderStatus.ACCEPTED,
                SupportBotMessage.ACCEPT_ORDER,
                helpers.get_accepted_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.ORDER_DETAIL.get("command"):
            await support_bot_handlers.send_order_detail(
                db,
                update,
                arg,
                lang,
            )
            return

        elif command == TelegramCallbackCommand.DECLINE_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db,
                update,
                arg,
                lang,
                OrderStatus.DECLINED,
                SupportBotMessage.DECLINE_ORDER,
                helpers.get_declined_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.DECLINE_PAYMENT_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db,
                update,
                arg,
                lang,
                OrderStatus.PAYMENT_DECLINED,
                SupportBotMessage.DECLINE_PAYMENT_ORDER,
                helpers.get_empty_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.PREPARE_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db,
                update,
                arg,
                lang,
                OrderStatus.PREPARATION,
                SupportBotMessage.PREPARE_ORDER,
                helpers.get_prepare_order_reply_markup,
            )
            return

        elif command == TelegramCallbackCommand.SEND_ORDER.get("command"):
            await support_bot_handlers.order_change_status_handler(
                db,
                update,
                arg,
                lang,
                OrderStatus.SENT,
                SupportBotMessage.SEND_ORDER,
                helpers.get_empty_reply_markup,
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
        update: telegram.Update = telegram.Update.de_json(data, bot=bot)

        if not update.message.text:
            return

        if update.message.text == TelegramSupportBotCommand.START["command"]:
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            if not shop_telegram_bot:
                text = helpers.get_start_support_bot_message(lang)
                reply_markup = helpers.get_start_support_bot_reply_markup(lang)
                await update.message.reply_text(text=text, reply_markup=reply_markup,
                                                parse_mode="HTML")
                return
            else:
                text = helpers.load_message(lang, "support_account_already_connected",
                                            shop_title=shop_telegram_bot.shop.title)
                await update.message.reply_text(text=text, parse_mode="HTML")
                return

        elif update.message.text == TelegramSupportBotCommand.SEARCH_ORDER["command"]:
            await update.message.reply_text(SupportBotMessage.ENTER_ORDER_NUMBER[lang],
                                            parse_mode="HTML")
            return

        elif update.message.text == TelegramSupportBotCommand.CREDIT_VIEW["command"]:
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            await support_bot_handlers.send_user_credit_information(db, update, shop_telegram_bot,
                                                                    lang)
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
                db,
                update,
                OrderStatus.PAYMENT_CHECK,
                helpers.get_order_message,
                helpers.get_payment_check_order_reply_markup,
                lang,
            )
            return
        elif update.message.text == TelegramSupportBotCommand.ACCEPTED_ORDERS["command"]:
            await support_bot_handlers.send_all_order_by_status(
                db,
                update,
                OrderStatus.ACCEPTED,
                helpers.get_order_message,
                helpers.get_accepted_order_reply_markup,
                lang,
            )
            return

        elif update.message.text == TelegramSupportBotCommand.UNPAID_ORDERS["command"]:
            await support_bot_handlers.send_all_order_by_status(
                db,
                update,
                OrderStatus.UNPAID,
                helpers.get_order_message,
                helpers.get_unpaid_order_reply_markup,
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


def get_or_create_lead(db: Session, telegram_bot_id, lead_data: telegram.User):
    lead = services.social.telegram_lead.get_by_chat_id(db, chat_id=lead_data.id,
                                                        telegram_bot_id=telegram_bot_id)
    if not lead:
        lead_number = services.social.telegram_lead.get_last_lead_number(
            db, telegram_bot_id=telegram_bot_id)
        lead = services.social.telegram_lead.create(
            db, obj_in=schemas.social.TelegramLeadCreate(
                telegram_bot_id=telegram_bot_id,
                chat_id=lead_data.id,
                first_name=lead_data.first_name,
                last_name=lead_data.last_name,
                username=lead_data.username,
                lead_number=lead_number + 1,
            ))
    return lead


async def telegram_bot_webhook_handler(db: Session, data: dict, bot_id: int, lang):
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return

    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))
    update = bot_handlers.get_update(data, bot)
    lead = get_or_create_lead(db, telegram_bot.id, update.message.from_user)
    mirror_message = None
    if helpers.is_start_message(data, bot):
        sent_message = await bot_handlers.handle_start_message(
            telegram_bot,
            update,
            lang,
        )
    else:
        chatbot_service = ChatBotTelegramBotService(ChatBotTelegramBotRepository(db))
        chatbot_telegram_bot = chatbot_service.get_by_telegram_bot_id(telegram_bot.id)

        if (chatbot_telegram_bot and lead.is_ai_answer
                and update.message.text not in TelegramBotCommand.commands_text):
            sent_message = await bot_handlers.handle_chatbot_qa(db, update,
                                                                chatbot_telegram_bot.chatbot_id)
        else:
            sent_message, mirror_message = await bot_handlers.handle_shop_message(
                db, telegram_bot.id, update, lead, lang)

    bot_handlers.save_lead_message(db, update, lead, mirror_message)
    if sent_message:
        bot_handlers.save_bot_message(db, sent_message, lead)


async def telegram_message_builder_bot_handler(db: Session, data: dict, lang):
    bot = Bot(settings.MESSAGE_BUILDER_BOT_TOKEN)

    if data.get("callback_query"):
        update = telegram.Update.de_json({
            "update_id": data["update_id"],
            **data["callback_query"]
        }, bot)

        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")
        if command == MessageBuilderButton.CANCEL_MESSAGE.get("command"):
            await message_builder_bot.cancel_message(db, lang, update, arg)
        elif command == MessageBuilderButton.FINISH_MESSAGE.get("command"):
            await message_builder_bot.finish_message(db, lang, update, arg)

        return

    update = telegram.Update.de_json(data, bot)
    if update.inline_query:
        if not update.inline_query.query:
            return

        message = services.message_builder.message.get_by_chat_id_and_id(
            db, id=int(update.inline_query.query), chat_id=update.inline_query.from_user.id)
        if message:
            await message_builder_bot.send_inline_query_answer(update, message)
        return

    if update.message.text == MessageBuilderCommand.START["command"]:
        message = helpers.load_message(lang, "message_builder_start")
        await update.message.reply_text(message)
    elif update.message.text == MessageBuilderCommand.NEW_MESSAGE["command"]:
        await message_builder_bot.create_new_message(db, lang, update)

    elif update.message.text == MessageBuilderCommand.CANCEL_MESSAGE["command"]:
        await message_builder_bot.cancel_message_check(db, lang, update)
    else:
        await message_builder_bot.build(db, update)

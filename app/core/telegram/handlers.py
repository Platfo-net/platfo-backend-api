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


def get_or_create_lead(db: Session, telegram_bot_id, lead_data):
    lead = services.social.telegram_lead.get_by_chat_id(db, chat_id=lead_data.get("id"),
                                                        telegram_bot_id=telegram_bot_id)
    if not lead:
        lead_number = services.social.telegram_lead.get_last_lead_number(
            db, telegram_bot_id=telegram_bot_id)
        lead = services.social.telegram_lead.create(
            db, obj_in=schemas.social.TelegramLeadCreate(
                telegram_bot_id=telegram_bot_id,
                chat_id=lead_data.get("id"),
                first_name=lead_data.get("first_name"),
                last_name=lead_data.get("last_name"),
                username=lead_data.get("username"),
                lead_number=lead_number + 1,
            ))
    return lead


async def telegram_bot_webhook_handler(db: Session, data: dict, bot_id: int, lang):
    telegram_bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if not telegram_bot:
        return

    bot = Bot(token=security.decrypt_telegram_token(telegram_bot.bot_token))
    if helpers.is_start_message(data, bot):
        await bot_handlers.handle_start_message(
            telegram_bot,
            bot,
            data,
            "fa",
        )
        return
    chatbot_service = ChatBotTelegramBotService(ChatBotTelegramBotRepository(db))

    chatbot_telegram_bot = chatbot_service.get_by_telegram_bot_id(telegram_bot.id)

    if chatbot_telegram_bot:
        await bot_handlers.handle_chatbot_qa(db, bot, data, chatbot_telegram_bot.chatbot_id,
                                             telegram_bot)
        return

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_telegram_bot_id(
        db, telegram_bot_id=telegram_bot.id)
    if data.get("callback_query"):
        lead_data = data["callback_query"]["from"]
        lead = get_or_create_lead(db, telegram_bot.id, lead_data)
        update = telegram.Update.de_json({
            "update_id": data["update_id"],
            **data["callback_query"]
        }, bot)

        callback = data.get("callback_query").get("data")
        command, arg = callback.split(":")
        if command == TelegramCallbackCommand.PAY_ORDER.get("command"):
            await bot_handlers.send_lead_pay_message(db, telegram_bot, lead, arg, lang)

    elif data.get("message"):
        lead_data = data["message"]["from"]
        lead = get_or_create_lead(db, telegram_bot.id, lead_data)

        reply_to_message = data["message"].get("reply_to_message")
        if reply_to_message:
            telegram_order = services.shop.telegram_order.get_by_reply_to_id_and_lead_id(
                db, lead_id=lead.id, reply_to_id=reply_to_message["message_id"])

            if not shop_telegram_bot:
                return

            if telegram_order:
                await bot_handlers.handle_order_payment(db, data, telegram_order,
                                                        shop_telegram_bot, bot, lang)
                return

        update = telegram.Update.de_json(data, bot)
        if update.message.text == TelegramBotCommand.VITRIN["command"]:

            if not shop_telegram_bot:
                return

            await update.message.reply_text(
                text="ویترین", reply_markup=helpers.get_shop_menu(shop_telegram_bot.shop.uuid,
                                                                  lead.uuid, lang),
                parse_mode="HTML")

        elif update.message.text == TelegramBotCommand.SEND_DIRECT_MESSAGE["command"]:
            text = helpers.load_message(lang, "lead_to_support_message_helper",
                                        lead_number=lead.lead_number)
            await update.message.reply_text(text=text, parse_mode="HTML")

        else:
            message = update.message.text
            bot = Bot(settings.SUPPORT_BOT_TOKEN)

            if not shop_telegram_bot:
                return

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

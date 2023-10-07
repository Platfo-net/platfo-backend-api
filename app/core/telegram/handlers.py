import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import schemas, services
from app.constants.order_status import OrderStatus
from app.constants.telegram_callback_command import TelegramCallbackCommand
from app.constants.telegram_support_bot_commands import \
    TelegramSupportBotCommand
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
        if command == TelegramCallbackCommand.ACCEPT_ORDER.get("command"):
            await support_bot_handlers.accept_order_handler(db, update, arg, lang)
            return

        elif command == TelegramCallbackCommand.DECLINE_ORDER.get("command"):
            await support_bot_handlers.decline_order_handler(db, update, arg, lang)
            return

        elif command == TelegramCallbackCommand.DECLINE_PAYMENT_ORDER.get("command"):
            await support_bot_handlers.decline_payment_order_handler(db, update, arg, lang)
            return

        elif command == TelegramCallbackCommand.PREPARE_ORDER.get("command"):
            await support_bot_handlers.prepare_order_handler(db, update, arg, lang)
            return

        elif command == TelegramCallbackCommand.SEND_ORDER.get("command"):
            await support_bot_handlers.send_order_handler(db, update, arg, lang)
            return

        elif command == TelegramCallbackCommand.ACCEPT_SHOP_SUPPORT_ACCOUNT.get("command"):
            await support_bot_handlers.verify_support_account(db, update, arg, lang)
            return
        elif command == TelegramCallbackCommand.SEND_DIRECT_MESSAGE.get("command"):
            await support_bot_handlers.send_lead_information_to_support_bot(db, update, arg, lang)
            return

    else:
        update: telegram.Update = telegram.Update.de_json(data, bot=bot)

        if update.message.text == TelegramSupportBotCommand.START["command"]:
            await update.message.reply_text(SupportBotMessage.ENTER_CODE[lang])
            return

        if update.message.text == TelegramSupportBotCommand.SEARCH_ORDER["command"]:
            await update.message.reply_text(SupportBotMessage.ENTER_ORDER_NUMBER[lang])
            return

        if update.message.text == TelegramSupportBotCommand.SEARCH_ORDER["command"]:
            message = helpers.load_message(lang, "direct_message_helper")
            await update.message.reply_text(message)
            return

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
                text = support_bot_handlers.get_payment_check_order_message(order, lang)
                reply_markup = support_bot_handlers.get_payment_check_order_reply_markup(
                    order, lang)
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
                text = support_bot_handlers.get_accepted_order_message(order, lang)
                reply_markup = support_bot_handlers.get_accepted_order_reply_markup(order, lang)

                await update.message.reply_text(
                    text,
                    reply_markup=reply_markup,
                )
            return
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
                text = support_bot_handlers.get_unpaid_order_message(order, lang)
                reply_markup = support_bot_handlers.get_unpaid_order_reply_markup(order, lang)

                await update.message.reply_text(
                    text, reply_markup=reply_markup
                )
            return
        elif update.message.text.isnumeric():
            order_number = int(update.message.text)
            await support_bot_handlers.send_order(db, update, order_number, lang)
            return
        else:
            code = update.message.text.lstrip().rstrip()
            if not len(code):
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return
            if len(code) != 8:
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return

            if not code[0] == "P":
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return
            support_account = services.shop.shop_telegram_bot.get_by_chat_id(
                db, chat_id=update.message.chat_id)
            if support_account:
                await update.message.reply_text(
                    SupportBotMessage.SUPPORT_ACCOUNT_ALREADY_CONNECTED[lang].format(
                        title=shop_telegram_bot.shop.title)
                )
                return

            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
                db, support_token=code)
            if not shop_telegram_bot:
                await update.message.reply_text(SupportBotMessage.WRONG_CODE[lang])
                return

            if shop_telegram_bot.support_account_chat_id:
                await update.message.reply_text(
                    SupportBotMessage.SHOP_ALREADY_CONNECTED[lang].format(
                        title=shop_telegram_bot.shop.title)
                )
                return

            text, reply_markup = support_bot_handlers.verify_shop_support_account_message(
                shop_telegram_bot, lang)
            await update.message.reply_text(
                text, reply_markup=reply_markup
            )
            services.shop.shop_telegram_bot.set_support_account_chat_id(
                db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)
            return


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
        reply_markup=bot_handlers.get_shop_menu(telegram_bot.uuid, shop_telegram_bot.shop.uuid)
    )

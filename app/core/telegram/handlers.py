from uuid import uuid4
import requests
import telegram
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.order_status import OrderStatus
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
        elif command == TelegramCallbackCommand.ACCEPT_ORDER.get("command"):
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
            await support_bot_handlers.send_direct_message_helper(db, update, arg, lang)
            return

    else:
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
            await handle_order_payment(db, data, telegram_order, shop_telegram_bot, bot, lang)
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


async def handle_order_payment(
    db: Session,
    data: dict,
    telegram_order: models.shop.ShopTelegramOrder,
    shop_telegram_bot: models.shop.ShopShopTelegramBot,
    bot: telegram.Bot,
    lang: str
):
    support_bot = Bot(settings.SUPPORT_BOT_TOKEN)
    if data["message"].get("photo"):
        # TODO handler_photo
        photo_unique_id = data["message"]["photo"][0]["file_id"]
        res: telegram.File = await bot.get_file(file_id=photo_unique_id)
        if not res.file_path:
            bot.send_message(
                chat_id=update["message"]["from"]["id"],
                text="فایل مشکل داره. دوباره تلاش کن"
            )
        file_path = res.file_path
        res = requests.get(file_path)
        if not res.status_code == 200:
            bot.send_message(
                chat_id=update["message"]["from"]["id"],
                text="فایل مشکل داره. دوباره تلاش کن"
            )
            return
        image_format = file_path.split(".")[-1]
        file_name = f"{uuid4()}.{image_format}"
        with open(file_name, "wb") as f:
            f.write(res.content)

        storage.add_file_to_s3(
            file_name, file_name, settings.S3_TELEGRAM_BOT_IMAGES_BUCKET)
        url = storage.get_object_url(file_name, settings.S3_TELEGRAM_BOT_IMAGES_BUCKET)
        
        await support_bot.send_photo(photo="http://141.98.210.31:9000/telegram/asd.png", chat_id=data["message"]["from"]["id"])
        return

    update = telegram.Update.de_json(bot, data)
    services.shop.telegram_order.add_message_text(
        db, telegram_order_id=telegram_order.id, text=update.message.text)
    await update.message.reply_text(
        text="شما پرداخت کردید",
        reply_to_message_id=telegram_order.bot_message_id,
    )
    await support_bot.send_message(
        text=f"این بنده خدا پرداخت کرد , {update.message.text}",
        chat_id=shop_telegram_bot.support_account_chat_id,
        reply_to_message_id=telegram_order.support_bot_message_id,
    )
    order = services.shop.order.get(db, id=telegram_order.order_id)
    order = services.shop.order.change_status(
        db, order=order, status=OrderStatus.PAYMENT_CHECK["value"])
    await support_bot.edit_message_text(
        text=support_bot_handlers.get_payment_check_order_message(order, lang),
        chat_id=shop_telegram_bot.support_account_chat_id,
        message_id=telegram_order.support_bot_message_id,
        reply_markup=support_bot_handlers.get_payment_check_order_reply_markup(
            order, lang),
        parse_mode="HTML"
    )

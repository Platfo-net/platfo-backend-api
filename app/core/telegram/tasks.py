import asyncio

import telegram
from pydantic import UUID4
from sqlalchemy.orm import Session
from telegram import Bot

from app import models, schemas, services
from app.constants.order_status import OrderStatus
from app.core.celery import celery
from app.core.config import settings
from app.db.session import SessionLocal


@celery.task
def telegram_support_bot_task(data):
    db = SessionLocal()
    try:
        asyncio.run(telegram_support_bot_handler(db, data))
    except Exception as e:
        print(e)

    db.close()


@celery.task
def telegram_webhook_task(data: dict, bot_id: int):
    db = SessionLocal()
    try:
        asyncio.run(telegram_bot_webhook_handler(db, data, bot_id=bot_id))
    except Exception as e:
        print(e)

    db.close()


@celery.task
def send_lead_order_to_bot_task(telegram_bot_id: int, lead_id: int, order_id: int):
    db = SessionLocal()
    try:
        asyncio.run(send_lead_order_to_bot_handler(db, telegram_bot_id, lead_id, order_id))
    except Exception as e:
        print(e)

    db.close()


@celery.task
def send_lead_order_to_shop_support_task(telegram_bot_id: int, lead_id: int, order_id: int):
    db = SessionLocal()
    try:
        asyncio.run(
            send_lead_order_to_shop_support_handler(
                db,
                telegram_bot_id,
                lead_id, order_id
            )
        )
    except Exception as e:
        print(e)

    db.close()


async def telegram_support_bot_handler(db: Session, data: dict):
    bot = telegram.Bot(settings.SUPPORT_BOT_TOKEN)
    if data.get("callback_query"):
        update = telegram.Update.de_json(
            {"update_id": data["update_id"], **data["callback_query"]}, bot
        )
        callback = data.get("callback_query").get("data")
        command, order_id = callback.split("-")
        if command == "ACCEPT_ORDER":
            order = services.shop.order.get_by_uuid(db, id=order_id)
            if not order:
                return

            order = services.shop.order.change_status(db, order=order, status=OrderStatus.ACCEPTED)
            await update.message.reply_text(
                f"order {order.order_number} accepted",
                reply_to_message_id=update.message.message_id
                )

    else:
        update: telegram.Update = telegram.Update.de_json(data, bot=bot)
        if update.message.text == "/start":
            await update.message.reply_text("Enter your code")

        elif update.message.text == "/orders":
            # TODO witch orders ??
            chat_id = update.message.chat_id
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_chat_id(db, chat_id=chat_id)

            if not shop_telegram_bot:
                await update.message.reply_text(
                    "Your account doesn't have any shop or not registered as support account"
                )
                return

            orders = services.shop.order.get_shop_orders(db, shop_id=shop_telegram_bot.shop_id)  # noqa
            text, reply_markup = get_order_message(orders[0])
            await update.message.reply_text(
                text, reply_markup=reply_markup
            )
            return
            # TODO send orders

        else:
            code = update.message.text.lstrip().rstrip()
            if len(code) != 8:
                await update.message.reply_text("Wrong code.")
                return
            shop_telegram_bot = services.shop.shop_telegram_bot.get_by_support_token(
                db, support_token=code)
            if not shop_telegram_bot:
                await update.message.reply_text("Wrong code.")
                return
            if shop_telegram_bot.is_support_verified:
                await update.message.reply_text(
                    f"Your shop '{shop_telegram_bot.shop.title}' is"
                    " already connected to an account.")
                return

            await update.message.reply_text(
                f"You are trying to connect your account to {shop_telegram_bot.shop.title} shop,\n"
                f"Enter this code in app: {shop_telegram_bot.support_bot_token}"
            )
            services.shop.shop_telegram_bot.set_support_account_chat_id(
                db, db_obj=shop_telegram_bot, chat_id=update.message.chat_id)


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
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int):
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

    m = f"No: {order.order_number}\nItems:"

    for item in order.items:
        m += f"\n {item.product.title}"

    bot = Bot(token=telegram_bot.bot_token)
    await bot.send_message(chat_id=lead.chat_id, text=m)
    return


async def send_lead_order_to_shop_support_handler(
        db: Session, telegram_bot_id: int, lead_id: int, order_id: int):

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

    m = f"No: {order.order_number}\nItems:"

    for item in order.items:
        m += f"\n {item.product.title}"
    bot = Bot(token=settings.SUPPORT_BOT_TOKEN)
    await bot.send_message(chat_id=shop_telegram_bot.support_account_chat_id, text=m)
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


def get_order_message(order: models.shop.ShopOrder):
    text = f"Order No: {order.order_number} \n"
    total_price = 0
    for item in order.items:
        text += f"{item.product.title} : {item.count}\n"
        total_price += item.product.price * item.count

    text += f"Total: {total_price}"

    keyboard = [
        [
            telegram.InlineKeyboardButton(
                "Accept order", callback_data=f"ACCEPT_ORDER-{order.uuid}")
        ]
    ]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    return text, reply_markup

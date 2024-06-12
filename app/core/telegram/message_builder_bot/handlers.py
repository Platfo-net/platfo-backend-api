from uuid import uuid4

import telegram
from sqlalchemy.orm import Session

from app import models, services
from app.constants.message_builder import MessageBuilderButton, MessageBuilderTelegramMessage, \
    MessageStatus
from app.core import storage
from app.core.config import settings
from app.core.telegram import helpers
from app.core.telegram.helpers.helpers import download_and_upload_telegram_image
from app.core.utils import generate_random_short_url


async def create_new_message(db: Session, lang, update: telegram.Update):

    message = services.message_builder.message.get_last_message(db, chat_id=update.message.chat_id,
                                                                status=MessageStatus.BUILDING)
    if message:
        await update.message.reply_text(
            text=MessageBuilderTelegramMessage.ERROR_NOT_FINISHED_MESSAGE_EXIST, parse_mode="HTML")
        return

    message = services.message_builder.message.create(db, chat_id=update.message.chat_id)

    text = helpers.load_message(
        lang,
        "message_builder_step_1",
        message_id=message.id,
    )

    await update.message.reply_text(text=text, parse_mode="HTML")


async def cancel_message_check(db: Session, lang, update: telegram.Update):

    message = services.message_builder.message.get_last_message(db, chat_id=update.message.chat_id,
                                                                status=MessageStatus.BUILDING)

    if not message:
        await update.message.reply_text(
            text=MessageBuilderTelegramMessage.ERROR_NOT_BUILDING_MESSAGE_EXIST, parse_mode="HTML")
        return

    keyboard = [[
        telegram.InlineKeyboardButton(
            MessageBuilderButton.CANCEL_MESSAGE["title"],
            callback_data=f"{MessageBuilderButton.CANCEL_MESSAGE['command']}:{message.id}"),
    ]]
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=MessageBuilderTelegramMessage.CANCEL_MESSAGE_CHECK,
                                    reply_markup=reply_markup)


async def cancel_message(db: Session, lang, update: telegram.Update, message_id):

    message = services.message_builder.message.get(db, id=int(message_id))
    if not message:
        await update.message.reply_text(text=MessageBuilderTelegramMessage.ERROR_MESSAGE_NOT_FOUND,
                                        parse_mode="HTML")
        return

    services.message_builder.message.remove(db, db_obj=message)
    await update.message.reply_text(text=MessageBuilderTelegramMessage.CANCEL_MESSAGE_SUCCESSFULLY)


async def finish_message(db: Session, lang, update: telegram.Update, message_id):

    message = services.message_builder.message.get(db, id=int(message_id))
    if not message:
        await update.message.reply_text(text=MessageBuilderTelegramMessage.ERROR_MESSAGE_NOT_FOUND,
                                        parse_mode="HTML")
        return

    services.message_builder.message.change_status(db, db_obj=message,
                                                   status=MessageStatus.FINISHED)
    await update.message.reply_text(text=MessageBuilderTelegramMessage.MESSAGE_CREATED_SUCCESSFULLY
                                    )


async def build(db: Session, update: telegram.Update):

    last_message = services.message_builder.message.get_last_message(
        db, chat_id=update.message.chat_id)

    if not last_message or last_message.status == MessageStatus.FINISHED:
        await update.message.reply_text(
            text=MessageBuilderTelegramMessage.ERROR_NOT_BUILDING_MESSAGE_EXIST)
        return

    if update.message.text:
        if not last_message.message_text:
            last_message.message_text = update.message.text
            await update.message.reply_text(text=MessageBuilderTelegramMessage.ENTER_URL)

        elif not last_message.url:
            last_message.url = update.message.text
            last_message.short_url = generate_random_short_url(6)
            await update.message.reply_text(
                text=MessageBuilderTelegramMessage.ENTER_URL_BUTTON_TEXT,
            )

        elif not last_message.button_title:
            last_message.button_title = update.message.text
            keyboard = [[
                telegram.InlineKeyboardButton(
                    MessageBuilderButton.FINISH_MESSAGE["title"],
                    callback_data=f"{MessageBuilderButton.FINISH_MESSAGE['command']}:{last_message.id}"),  # noqa
            ]]
            reply_markup = telegram.InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text=MessageBuilderTelegramMessage.ENTER_IMAGE,
                                            reply_markup=reply_markup)

    elif update.message.photo:
        image = update.message.photo[-1].file_id
        url, file_name = await download_and_upload_telegram_image(
            update.get_bot(), image, settings.S3_MESSAGE_BUILDER_IMAGE_BUCKET)
        last_message.image = file_name
        last_message.status = MessageStatus.FINISHED

        await update.message.reply_text(
            text=MessageBuilderTelegramMessage.MESSAGE_CREATED_SUCCESSFULLY,
        )

    db.add(last_message)
    db.commit()
    db.refresh(last_message)


async def send_inline_query_answer(update: telegram.Update,
                                   message: models.message_builder.MessageBuilderMessage):
    print(message.button_title)
    if message.image:

        image_url = storage.get_object_url(message.image,
                                           bucket_name=settings.S3_MESSAGE_BUILDER_IMAGE_BUCKET)
        await update.inline_query.answer(
            results=[
                telegram.InlineQueryResultPhoto(
                    id=uuid4(), title=f"{message.message_text[:30]}...", photo_url=image_url,
                    thumbnail_url=image_url, caption=message.message_text,
                    reply_markup=telegram.InlineKeyboardMarkup([[
                        telegram.InlineKeyboardButton(
                            text=message.button_title or "Page", url=f"{settings.MESSAGE_BUILDER_WEBAPP_BASE_URL}?startapp={message.short_url}",  # noqa
                        )
                    ]]))
            ],
        )
    else:

        await update.inline_query.answer(results=[
            telegram.InlineQueryResultArticle(
                id=uuid4(), title=f"{message.message_text[:20]} ...",
                input_message_content=telegram.InputTextMessageContent(message.message_text),
                reply_markup=telegram.InlineKeyboardMarkup([[
                    telegram.InlineKeyboardButton(
                        text=message.button_title or "Page",
                        url=f"{settings.MESSAGE_BUILDER_WEBAPP_BASE_URL}?startapp={message.short_url}",  # noqa
                    )
                ]]))
        ])

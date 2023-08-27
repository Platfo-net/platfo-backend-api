import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.config import settings
from app.core.exception import raise_http_exception
import telegram
router = APIRouter(prefix='/telegram', tags=['Teleegram'])


async def get_me(token):
    bot = telegram.Bot(token=token)
    user = await bot.get_me()
    return {"first_name": user.first_name, "username": user.username, "id": user.id}


async def set_webhook(token):
    bot = telegram.Bot(token=token)
    res = await bot.set_webhook(f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/telegram/webhook")
    return res


@router.post('/', response_model=schemas.TelegramBot)
def connect_telegram_bot(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.ConnectTelegramBot,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    try:
        bot_information = asyncio.run(get_me(obj_in.bot_token))
    except telegram.error.InvalidToken:
        raise_http_exception(Error.INVALID_TELEGRAM_BOT)

    bot = services.telegram_bot.get_by_id(db, bot_id=bot_information["id"])
    if bot:
        raise_http_exception(Error.TELEGRAM_BOT_EXIST_IN_SYSTEM)

    try:
        res = asyncio.run(set_webhook(obj_in.bot_token))
    except Exception:
        raise_http_exception(Error.TELEGRAM_SERVER_SET_WEBHOOK_ERROR)

    if not res:
        raise_http_exception(Error.TELEGRAM_SERVER_SET_WEBHOOK_ERROR)

    bot_in = schemas.TelegramBotCreate(
        app_id=obj_in.app_id,
        app_secret=obj_in.app_secret,
        bot_token=obj_in.bot_token,
        first_name=bot_information["first_name"],
        username=bot_information["username"],
        bot_id=bot_information["bot_id"],
    )
    bot = services.telegram_bot.create(db, obj_in=bot_in, user_id=current_user.id)

    return schemas.TelegramBot(
        first_name=bot.first_name,
        username=bot.username,
    )

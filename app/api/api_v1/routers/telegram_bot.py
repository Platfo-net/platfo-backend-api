import asyncio
from typing import Any, List

import telegram
from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session
from app.core import storage

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.constants.telegram_bot_command import TelegramBotCommand
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/telegram', tags=['Telegram'])


async def get_me(token):
    bot = telegram.Bot(token=token)
    user = await bot.get_me()
    return {"first_name": user.first_name, "username": user.username, "bot_id": str(user.id)}


async def set_webhook(token, bot_id):
    bot = telegram.Bot(token=token)
    await bot.set_webhook(
        f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/webhook/telegram/bot/{bot_id}"
    )
    await bot.set_my_commands(
        commands=[
            telegram.BotCommand(
                command["command"],
                command["description"],
            ) for command in TelegramBotCommand.commands
        ]
    )
    return True


@router.post('', response_model=schemas.TelegramBot)
def add_telegram_bot(
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
    bot_id = bot_information["bot_id"]
    bot = services.telegram_bot.get_by_bot_id(db, bot_id=bot_id)
    if bot:
        raise_http_exception(Error.TELEGRAM_BOT_EXIST_IN_SYSTEM)

    try:
        res = asyncio.run(set_webhook(obj_in.bot_token, bot_id))

    except Exception:
        raise_http_exception(Error.TELEGRAM_SERVER_SET_WEBHOOK_ERROR)

    if not res:
        raise_http_exception(Error.TELEGRAM_SERVER_SET_WEBHOOK_ERROR)

    bot_in = schemas.TelegramBotCreate(
        bot_token=obj_in.bot_token,
        first_name=bot_information["first_name"],
        username=bot_information["username"],
        bot_id=bot_information["bot_id"],
    )
    bot = services.telegram_bot.create(db, obj_in=bot_in, user_id=current_user.id)

    return schemas.TelegramBot(
        id=bot.uuid,
        first_name=bot.first_name,
        username=bot.username,
    )


@router.put('/{id}', response_model=schemas.TelegramBot)
def update_bot(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.TelegramBotUpdate,
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    bot = services.telegram_bot.get_by_uuid(db, uuid=id)

    if not bot:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND)

    if bot.user_id != current_user.id:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND_ACCESS_DENIED)

    new_bot = services.telegram_bot.update(db, db_obj=bot, obj_in=obj_in)

    image_url = storage.get_object_url(
        new_bot.image, settings.S3_TELEGRAM_BOT_MENU_IMAGES_BUCKET)

    return schemas.TelegramBot(
        id=new_bot.uuid,
        first_name=new_bot.first_name,
        username=new_bot.username,
        welcome_message=new_bot.welcome_message,
        button_name=new_bot.button_name,
        app_link=new_bot.app_link,
        image=new_bot.image,
        image_url=image_url,
    )


@router.get('/all', response_model=List[schemas.TelegramBot])
def get_telegram_bots_list(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    bots = services.telegram_bot.get_multi_by_user_id(db, user_id=current_user.id)

    return [schemas.TelegramBot(
        id=bot.uuid,
        first_name=bot.first_name,
        username=bot.username,
    ) for bot in bots]


@router.get('/{id}', response_model=schemas.TelegramBot)
def get_telegram_bot(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:
    bot = services.telegram_bot.get_by_uuid(db, uuid=id)
    if not bot:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND)
    if bot.user_id != current_user.id:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUND_ACCESS_DENIED)

    image_url = storage.get_object_url(
        bot.image, settings.S3_TELEGRAM_BOT_MENU_IMAGES_BUCKET)

    return schemas.TelegramBot(
        id=bot.uuid,
        first_name=bot.first_name,
        username=bot.username,
        button_name=bot.button_name,
        app_link=bot.app_link,
        image=bot.image,
        image_url=image_url,
    )


@router.get('/{shop_id}/all', response_model=schemas.social.TelegramLeadListItem)
def get_telegram_bot_leads(
        *,
        db: Session = Depends(deps.get_db),
        shop_id: UUID4,
        page: int = 1,
        page_size: int = 20,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
) -> Any:
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop.id
    )
    leads, pagination = services.social.telegram_lead. \
        get_multi_by_telegram_bot_id(db,
                                     telegram_bot_id=shop_telegram_bot.telegram_bot_id,
                                     page=page,
                                     page_size=page_size
                                     )

    lead_items = [
        schemas.social.TelegramLead(
            chat_id=lead.chat_id,
            first_name=lead.first_name,
            last_name=lead.last_name,
            username=lead.username,
            lead_number=lead.lead_number,
        )
        for lead in leads
    ]

    return schemas.social.TelegramLeadListItem(
        items=lead_items,
        pagination=pagination
    )

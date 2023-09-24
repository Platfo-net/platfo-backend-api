import asyncio

import telegram
from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.api.api_v1.routers.telegram_bot import get_me, set_webhook
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.core.utils import generate_random_token

router = APIRouter(prefix='/telegram')


@router.post('/create-shop', response_model=schemas.shop.ShopTelegramBotRegister)
def create_shop_for_telegram_bot(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.ShopCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):

    shop = services.shop.shop.get_by_title(db, title=obj_in.title.lstrip().rstrip())

    if shop and shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_SHOP_IS_EXIST)

    support_token = generate_random_token(length=8)

    while services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=support_token
    ):
        support_token = generate_random_token(length=8)

    support_bot_token = generate_random_token(length=8)

    while services.shop.shop_telegram_bot.get_by_support_bot_token(
            db, support_bot_token=support_bot_token
    ):
        support_bot_token = generate_random_token(length=8)

    shop = services.shop.shop.create(
        db,
        obj_in=obj_in,
        user_id=current_user.id
    )

    shop_telegram_bot = services.shop.shop_telegram_bot.create(
        db,
        obj_in=schemas.shop.shop_telegram_bot.ShopTelegramBotCreate(
            support_token=support_token,
            support_bot_token=support_bot_token,
            shop_id=shop.id,
        )
    )

    return schemas.shop.ShopTelegramBotRegister(
        id=shop.uuid,
        title=shop.title,
        category=shop.category,
        description=shop.description,
        support_token=shop_telegram_bot.support_token,
    )


@router.post('/connect-support-account', status_code=status.HTTP_200_OK)
def connect_shop_to_support_account(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.ShopConnectSupport,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=obj_in.shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)

    if shop_telegram_bot.is_support_verified:
        raise_http_exception(Error.SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_SUPPORT_ACCOUNT)

    if shop_telegram_bot.support_bot_token != obj_in.token:
        raise_http_exception(Error.SHOP_INVALID_SUPPORT_TOKEN)

    shop = services.shop.shop_telegram_bot.verify_support_account(db, db_obj=shop_telegram_bot)

    return


@router.post('/connect-bot', status_code=status.HTTP_200_OK)
def connect_shop_to_telegram_bot(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.ShopConnectTelegramBot,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=obj_in.shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    telegram_bot = services.telegram_bot.get_by_bot_token(db, token=obj_in.bot_token)

    if telegram_bot:
        raise_http_exception(Error.TELEGRAM_BOT_EXIST_IN_SYSTEM)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)

    if shop_telegram_bot.telegram_bot_id:
        raise_http_exception(Error.SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_TELEGRAM_BOT)

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

    services.shop.shop_telegram_bot.connect_telegram_bot(
        db, db_obj=shop_telegram_bot, telegram_bot_id=bot.id)

    return


@router.get('/{shop_id}/check-support-bot', status_code=status.HTTP_200_OK)
def check_shop_is_connected_to_support_account(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)

    if not shop_telegram_bot.support_account_chat_id:
        raise_http_exception(Error.SHOP_DOESNT_HAVE_SUPPORT_ACCOUNT)

    return

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
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
        support_token=support_token,
        support_bot_token=support_bot_token,
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
    if shop_telegram_bot.support_account_chat_id:
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

    telegram_bot = services.telegram_bot.get_by_uuid(db, uuid=obj_in.bot_id)

    if not telegram_bot:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUNT)

    if telegram_bot.user_id != current_user.id:
        raise_http_exception(Error.TELEGRAM_BOT_NOT_FOUNT_ACCESS_DENIED)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)

    if shop_telegram_bot.telegram_bot_id:
        raise_http_exception(Error.SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_TELEGRAM_BOT)

    shop = services.shop.shop_telegram_bot.connect_telegram_bot(
        db, db_obj=shop_telegram_bot, telegram_bor_id=telegram_bot.id)

    return

from typing import List

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.constants.shop_category import ShopCategory
from app.core.exception import raise_http_exception
from app.core.unit_of_work import UnitOfWork
from app.core.utils import generate_random_support_token

router = APIRouter(prefix='/shop', tags=["Shop Shop"])


@router.get('/all', response_model=List[schemas.shop.Shop])
def get_shop_multi(
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
):
    shops = services.shop.shop.get_multi_by_user(db, user_id=current_user.id)

    return [
        schemas.shop.Shop(
            id=shop.uuid,
            title=shop.title,
            category=shop.category,
            description=shop.description,
            is_info_required=shop.is_info_required,
            color_code=shop.theme[0].color_code if shop.theme else None,
        ) for shop in shops]


@router.get('/{id}', response_model=schemas.shop.Shop)
def get_shop(
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
):
    shop = services.shop.shop.get_by_uuid(db, uuid=id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    return schemas.shop.Shop(
        id=shop.uuid,
        title=shop.title,
        category=shop.category,
        description=shop.description,
        is_info_required=shop.is_info_required,
        color_code=shop.theme[0].color_code if shop.theme else None
    )


@router.put('/{id}', response_model=schemas.shop.Shop)
def update_shop(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.shop.ShopUpdate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    if obj_in.category not in ShopCategory.items:
        raise raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    def _handle_shop_theme_logic(db, obj_in, shop):
        if obj_in.color_code:
            shop_theme = services.shop.shop_theme.get_by_shop_id(db, shop_id=shop.id)
            if shop_theme:
                new_shop_theme = services.shop.shop_theme.update(
                    db,
                    db_obj=shop_theme, obj_in=obj_in)
                return new_shop_theme.color_code
            else:
                new_shop_theme = services.shop.shop_theme.create(
                    db, obj_in=obj_in, shop_id=shop.id
                )
                return new_shop_theme.color_code
        return None

    new_shop = services.shop.shop.update(db, db_obj=shop, obj_in=obj_in)

    color_code = _handle_shop_theme_logic(db, obj_in=obj_in, shop=shop)

    return schemas.shop.Shop(
        id=new_shop.uuid,
        title=new_shop.title,
        category=new_shop.category,
        description=new_shop.description,
        is_info_required=new_shop.is_info_required,
        color_code=color_code
    )


@router.get('/{id}/state', response_model=schemas.shop.ShopState)
def get_shop_telegram_state(
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
):
    shop = services.shop.shop.get_by_uuid(db, uuid=id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)

    if not shop_telegram_bot:
        support_token = generate_random_support_token(length=7)

        while services.shop.shop_telegram_bot.get_by_support_token(
            db, support_token=support_token
        ):
            support_token = generate_random_support_token(length=7)

        support_bot_token = generate_random_support_token(length=7)

        while services.shop.shop_telegram_bot.get_by_support_bot_token(
            db, support_bot_token=support_bot_token
        ):
            support_bot_token = generate_random_support_token(length=7)
        with UnitOfWork(db) as uow:
            shop_telegram_bot = services.shop.shop_telegram_bot.create(
                uow,
                obj_in=schemas.shop.shop_telegram_bot.ShopTelegramBotCreate(
                    support_token=support_token,
                    support_bot_token=support_bot_token,
                    shop_id=shop.id,
                )
            )

    shop_credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop.id)

    if not shop_credit:
        with UnitOfWork(db) as uow:
            services.credit.shop_credit.create(uow, shop_id=shop.id, free_days=7)

    return schemas.shop.ShopState(
        is_connected_to_support_bot=True if shop_telegram_bot.support_account_chat_id else False,
        is_connected_to_bot=True if shop_telegram_bot.telegram_bot else False,
        is_connected_to_bot_verified=shop_telegram_bot.is_support_verified,
    )


@router.get('/telegram/info/{id}', response_model=schemas.shop.ShopView)
def get_shop_for_telegram_shop(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
):
    shop = services.shop.shop.get_by_uuid(db, uuid=id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    return schemas.shop.ShopView(
        id=shop.uuid,
        title=shop.title,
        color_code=shop.theme[0].color_code if shop.theme else None
    )

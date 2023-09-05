from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.core.utils import generate_random_token

router = APIRouter(prefix='/shop')


@router.post('', response_model=schemas.shop.ShopRegister)
def create_shop(
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

    support_token = generate_random_token(length=8)

    while services.shop.shop.get_by_support_token(db, support_token=support_token):
        support_token = generate_random_token(length=8)

    support_bot_token = generate_random_token(length=8)

    while services.shop.shop.get_by_support_bot_token(db, support_bot_token=support_bot_token):
        support_bot_token = generate_random_token(length=8)

    shop = services.shop.shop.create(
        db, obj_in=obj_in, support_token=support_token, support_bot_token=support_bot_token, user_id=current_user.id)

    return schemas.shop.ShopRegister(
        id=shop.uuid,
        title=shop.title,
        category=shop.category,
        description=shop.description,
        support_token=shop.support_token,
    )


@router.get('/all', response_model=schemas.shop.Shop)
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

    return [schemas.shop.Shop(
        id=shop.uuid,
        title=shop.title,
        category=shop.category,
        description=shop.description,
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
        description=shop.description
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

    if shop.support_account_chat_id:
        raise_http_exception(Error.SHOP_SHOP_HAS_BEEN_ALREADY_CONNECTED_TO_SUPPORT_ACCOUNT)

    return schemas.shop.Shop(
        id=shop.uuid,
        title=shop.title,
        category=shop.category,
        description=shop.description
    )

from typing import List

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/shop')


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

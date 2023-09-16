

from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/categories')


@router.post('', response_model=schemas.shop.Category)
def create_category(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.CategoryCreate,
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

    category = services.shop.category.create(
        db,
        obj_in=obj_in,
        shop_id=shop.id,
    )
    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
    )


@router.put('/{id}', response_model=schemas.shop.Category)
def update_category(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.CategoryUpdate,
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
    category = services.shop.category.get_by_uuid(db, uuid=id)
    if not category:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    if category.user_id != current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

    category = services.shop.category.update(db, db_obj=category, obj_in=obj_in)
    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
    )


@router.get('/all', response_model=List[schemas.shop.Category])
def get_categories(
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
    categories = services.shop.category.get_multi_by_user(db, user_id=current_user.id)

    return [
        schemas.shop.Category(
            id=category.uuid,
            title=category.title,
        )
        for category in categories
    ]


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_category(
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

    category = services.shop.category.get_by_uuid(db, uuid=id)
    if not category:
        raise_http_exception(Error.CATEGORY_NOT_FOUND)

    if category.shop.user_id != current_user.id:
        raise_http_exception(Error.CAMPAIGN_NOT_FOUND_ACCESS_DENIED)

    services.shop.category.delete(db, db_obj=category)

    return

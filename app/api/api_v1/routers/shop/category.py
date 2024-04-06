from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.exception import raise_http_exception
from app.core.unit_of_work import UnitOfWork

router = APIRouter(prefix='/categories', tags=["Shop Category"])


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

    if not shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    with UnitOfWork(db) as uow:
        category = services.shop.category.create(
            uow,
            obj_in=obj_in,
            shop_id=shop.id,
        )
    image_url = storage.get_object_url(category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)

    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
        image=category.image,
        image_url=image_url
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

    if not category.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

    with UnitOfWork(db) as uow:
        category = services.shop.category.update(
            uow, db_obj=category, obj_in=obj_in)

    image_url = storage.get_object_url(category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)

    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
        image=category.image,
        image_url=image_url,
    )


@router.get('/{shop_id}/all', response_model=List[schemas.shop.Category])
def get_categories(
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

    categories = services.shop.category.get_multi_by_shop(db, shop_id=shop.id)

    return [
        schemas.shop.Category(
            id=category.uuid,
            title=category.title,
            image=category.image,
            image_url=storage.get_object_url(
                category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)
        )
        for category in categories
    ]


@router.get('/{id}', response_model=schemas.shop.Category)
def get_category(
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
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    if not category.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

    image_url = storage.get_object_url(category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)

    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
        image=category.image,
        image_url=image_url,
    )


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
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    if not category.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

    has_with_category = services.shop.product.has_with_category(
        db, category_id=category.id)
    if has_with_category:
        raise_http_exception(Error.SHOP_CATEGORY_HAS_PRODUCT_ERROR)
    else:
        storage.remove_file_from_s3(category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)
        with UnitOfWork(db) as uow:
            services.shop.category.hard_delete(uow, db_obj=category)

    return


@router.get('/telegram/{shop_id}/all', response_model=List[schemas.shop.Category])
def get_telegram_shop_categories(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
):

    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    categories = services.shop.category.get_multi_by_shop(db, shop_id=shop.id)

    return [
        schemas.shop.Category(
            title=category.title,
            id=category.uuid,
            image=category.image,
            image_url=storage.get_object_url(
                category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)
        )for category in categories
    ]


@router.get('/telegram/{shop_id}/{category_id}', response_model=schemas.shop.Category)
def get_telegram_shop_category(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    category_id: UUID4,
):

    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    category = services.shop.category.get_by_uuid(db, uuid=category_id)

    if not category:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)
    if not shop.id == category.shop_id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

    image_url = storage.get_object_url(category.image, settings.S3_SHOP_CATEGORY_IMAGE_BUCKET)

    return schemas.shop.Category(
        title=category.title,
        id=category.uuid,
        image=category.image,
        image_url=image_url,
    )

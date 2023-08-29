

from typing import List

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/products')


@router.post('', response_model=schemas.shop.Product)
def create_product(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.ProductCreate,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    category = services.shop.category.get_by_uuid(db, uuid=obj_in.category_id)
    if not category or category.user_id != current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    product = services.shop.product.create(db, obj_in=obj_in, user_id=current_user.id)

    image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)

    return schemas.shop.Product(
        id=product.uuid,
        title=product.title,
        price=product.price,
        image=image_url,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category=schemas.shop.Category(
            id=product.category.uuid,
            title=product.category.title,
        )
    )


@router.put('/{id}', response_model=schemas.shop.Product)
def update_update(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.ProductUpdate,
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

    product = services.shop.product.get_by_uuid(db, uuid=id)
    if not product or product.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR)

    category = services.shop.category.get_by_uuid(db, uuid=id)
    if not category or category.user_id != current_user.id:
        raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

    product = services.shop.product.update(db, db_obj=product, obj_in=obj_in)
    image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)

    return schemas.shop.Product(
        id=product.uuid,
        title=product.title,
        price=product.price,
        image=image_url,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category=schemas.shop.Category(
            id=product.category.uuid,
            title=product.category.title,
        )
    )


@router.get('/all', response_model=List[schemas.shop.Product])
def get_products(
    *,
    db: Session = Depends(deps.get_db),
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
):
    items, pagination = services.shop.product.get_multi_by_user(db, user_id=current_user.id)

    products_list = []
    for product in items:
        image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)
        products_list.append(
            schemas.shop.Product(
                id=product.uuid,
                title=product.title,
                price=product.price,
                image=image_url,
                created_at=product.created_at,
                updated_at=product.updated_at,
                category=schemas.shop.Category(
                    id=product.category.uuid,
                    title=product.category.title,
                )
            ))

    return schemas.shop.ProductListAPI(
        items=products_list,
        pagination=pagination,
    )

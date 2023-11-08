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
from app.core.telegram.helpers import has_credit_by_shop_id
from app.core.unit_of_work import UnitOfWork

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
    category = None
    shop = None

    if not (obj_in.shop_id or obj_in.category_id):
        raise_http_exception(Error.SHOP_CATEGORY_OR_SHOP_NOT_PROVIDED)

    elif not obj_in.shop_id and obj_in.category_id:
        category = services.shop.category.get_by_uuid(db, uuid=obj_in.category_id)
        if not category:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

        shop = services.shop.shop.get(db, id=category.shop_id)

    elif not obj_in.category_id and obj_in.shop_id:
        shop = services.shop.shop.get_by_uuid(db, uuid=obj_in.shop_id)

        if not shop:
            raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

        if shop.user_id != current_user.id:
            raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)
    else:
        category = services.shop.category.get_by_uuid(db, uuid=obj_in.category_id)
        shop = services.shop.shop.get_by_uuid(db, uuid=obj_in.shop_id)

        if not shop:
            raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

        if shop.user_id != current_user.id:
            raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

        if not category:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)

        if category.shop.user_id != current_user.id:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

        if category.shop_id != shop.id:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_IN_THIS_SHOP)

    with UnitOfWork(db) as uow:
        product = services.shop.product.create(
            uow,
            obj_in=obj_in,
            shop_id=shop.id,
            category_id=category.id if category else None
        )

    image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)

    cat = None
    if category:
        cat = schemas.shop.Category(
            id=product.category.uuid,
            title=product.category.title,
        )

    return schemas.shop.Product(
        id=product.uuid,
        title=product.title,
        price=product.price,
        currency=product.currency,
        image=image_url,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category=cat
    )


@router.put('/{id}', response_model=schemas.shop.Product)
def update_product(
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
    if not product:
        raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR)

    if product.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR_ACCESS_DENIED)
    category = None
    if obj_in.category_id:
        category = services.shop.category.get_by_uuid(db, uuid=obj_in.category_id)
        if not category:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR)
        if category.shop.user_id != current_user.id:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_ERROR_ACCESS_DENIED)

        if category.shop_id != product.shop_id:
            raise_http_exception(Error.SHOP_CATEGORY_NOT_FOUND_IN_THIS_SHOP)

    with UnitOfWork(db) as uow:
        product = services.shop.product.update(
            uow, db_obj=product, obj_in=obj_in, category_id=category.id if category else None)

    image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)

    cat = None
    if category:
        cat = schemas.shop.Category(
            id=product.category.uuid,
            title=product.category.title,
        )
    return schemas.shop.Product(
        id=product.uuid,
        title=product.title,
        price=product.price,
        currency=product.currency,
        image=image_url,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category=cat

    )


@router.get('/{shop_id}/all', response_model=schemas.shop.ProductListAPI)
def get_shop_products(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
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

    items, pagination = services.shop.product.get_multi_by_shop_id(
        db, shop_id=shop.id, page=page, page_size=page_size)

    products_list = []
    for product in items:
        image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)
        category = None
        if product.category_id:
            category = schemas.shop.Category(
                id=product.category.uuid,
                title=product.category.title,
            )
        products_list.append(
            schemas.shop.Product(
                id=product.uuid,
                title=product.title,
                price=product.price,
                image=image_url,
                currency=product.currency,
                created_at=product.created_at,
                updated_at=product.updated_at,
                category=category
            ))

    return schemas.shop.ProductListAPI(
        items=products_list,
        pagination=pagination,
    )


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_product(
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

    product = services.shop.product.get_by_uuid(db, uuid=id)
    if not product:
        raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR)

    if product.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR_ACCESS_DENIED)

    has_order_items = services.shop.order_item.has_item_with_product_id(db, product_id=product.id)
    with UnitOfWork(db) as uow:
        if has_order_items:
            services.shop.product.soft_delete(uow, db_obj=product)
        else:
            services.shop.product.hard_delete(uow, db_obj=product)

    return


@router.get('/{shop_id}/telegram-shop', response_model=schemas.shop.ProductListAPI)
def get_shop_products_for_telegram_shop(
    *,
    db: Session = Depends(deps.get_db),
    page: int = 1,
    page_size: int = 20,
    shop_id: UUID4,
):

    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if not has_credit_by_shop_id(db, shop.id):
        raise_http_exception(Error.SHOP_SHOP_NOT_AVAILABLE)

    items, pagination = services.shop.product.get_multi_by_shop_id(
        db, shop_id=shop.id, page=page, page_size=page_size, is_active=True)

    products_list = []
    for product in items:
        image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)
        category = None
        if product.category_id:
            category = schemas.shop.Category(
                id=product.category.uuid,
                title=product.category.title,
            )
        products_list.append(
            schemas.shop.Product(
                id=product.uuid,
                title=product.title,
                price=product.price,
                image=image_url,
                currency=product.currency,
                created_at=product.created_at,
                updated_at=product.updated_at,
                category=category
            ))

    return schemas.shop.ProductListAPI(
        items=products_list,
        pagination=pagination,
    )


@router.get('/{shop_id}/{product_id}', response_model=schemas.shop.ProductGetApi)
def get_shop_product(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    product_id: UUID4,
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

    product = services.shop.product.get_by_uuid(db, uuid=product_id)

    image_url = storage.get_object_url(product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET)
    category = None
    if product.category_id:
        category = schemas.shop.Category(
            id=product.category.uuid,
            title=product.category.title,
        )
    return schemas.shop.ProductGetApi(
        id=product.uuid,
        title=product.title,
        price=product.price,
        image=image_url,
        currency=product.currency,
        created_at=product.created_at,
        updated_at=product.updated_at,
        category=category,
        image_id=product.image,
    )

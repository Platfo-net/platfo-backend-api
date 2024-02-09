from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.config import settings
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/tables', tags=["Shop Table"])


@router.post('', response_model=schemas.shop.Table)
def create_table(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.TableCreate,
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

    table = services.shop.table.create(
        db,
        obj_in=obj_in,
        shop_id=shop.id,
    )

    return schemas.shop.Table(
        id=table.uuid,
        title=table.title
    )


@router.put('/{id}', response_model=schemas.shop.Table)
def update_table(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.TableUpdate,
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
    table = services.shop.table.get_by_uuid(db, uuid=id)
    if not table:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ERROR)

    if not table.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ACCESS_DENIED_ERROR)

    table = services.shop.table.update(
        db, db_obj=table, obj_in=obj_in)

    return schemas.shop.Table(
        title=table.title,
        id=table.uuid,
    )


@router.get('/{shop_id}/all', response_model=List[schemas.shop.TableItem])
def get_tables(
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

    tables = services.shop.table.get_multi_by_shop_id(db, shop_id=shop.id)

    return [
        schemas.shop.Table(
            id=table.uuid,
            title=table.title,
            url=f"{settings.PLATFO_SHOPS_BASE_URL}/{shop_id}?table={table.uuid}"
        )
        for table in tables
    ]


@router.get('/{table_id}', response_model=schemas.shop.TableItem)
def get_table(
    *,
    db: Session = Depends(deps.get_db),
    table_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):
    table = services.shop.table.get_by_uuid(db, uuid=table_id)
    if not table:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ERROR)

    if table.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ACCESS_DENIED_ERROR)

    return schemas.shop.Table(
        id=table.uuid,
        title=table.title,
        url=f"{settings.PLATFO_SHOPS_BASE_URL}/{table.shop.uuid}?table={table.uuid}"
    )


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_table(
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

    table = services.shop.category.get_by_uuid(db, uuid=id)
    if not table:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ERROR)

    if not table.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ACCESS_DENIED_ERROR)

    if services.shop.order.has_order_with_table(db, table.id):
        raise_http_exception(Error.SHOP_TABLE_NOT_FOUND_ACCESS_DENIED_ERROR)

    return

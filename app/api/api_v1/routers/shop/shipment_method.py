from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.core.unit_of_work import UnitOfWork

router = APIRouter(prefix='/shipment-methods')


@router.post('', response_model=schemas.shop.ShipmentMethod)
def create_shipment_method(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.shop.ShipmentMethodCreate,
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

    shop_shipment_method = services.shop.shipment_method.create(
        db,
        obj_in=obj_in,
        shop_id=shop.id
    )
    schemas.shop.ShipmentMethod(
        id=shop_shipment_method.uuid,
        title=shop_shipment_method.title,
        price=shop_shipment_method.price,
        currency=shop_shipment_method.currency,
        is_active=shop_shipment_method.is_active,
    )


@router.get('/{shop_id}/all', response_model=List[schemas.shop.ShipmentMethod])
def get_shop_shipment_methods(
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

    shop_shipment_methods = services.shop.shipment_method.get_multi_by_shop_id(db, shop_id=shop.id)

    return [
        schemas.shop.ShipmentMethod(
            id=shipment.uuid,
            title=shipment.title,
            price=shipment.price,
            currency=shipment.currency,
            is_active=shipment.is_active,
        )
        for shipment in shop_shipment_methods
    ]


@router.get('/{id}', response_model=schemas.shop.ShipmentMethod)
def get_shipment_method(
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
    shop_shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shop_shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shop_shipment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    return schemas.shop.ShipmentMethod(
        id=shop_shipment_method.uuid,
        title=shop_shipment_method.title,
        price=shop_shipment_method.price,
        currency=shop_shipment_method.currency,
        is_active=shop_shipment_method.is_active,
    )


@router.put('/{id}', response_model=schemas.shop.ShipmentMethod)
def update_shipment_method(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.shop.ShipmentMethodUpdate,
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
    shop_shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shop_shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shop_shipment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    shop_shipment_method = services.shop.shipment_method.update(
        db, db_obj=shop_shipment_method, obj_in=obj_in)

    schemas.shop.ShipmentMethod(
        id=shop_shipment_method.uuid,
        title=shop_shipment_method.title,
        price=shop_shipment_method.price,
        currency=shop_shipment_method.currency,
        is_active=shop_shipment_method.is_active,
    )


@router.put('/{id}/change-is-active', status_code=status.HTTP_200_OK)
def change_shop_shipment_method_is_active(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        obj_in: schemas.shop.ChangeShipmentIsActive,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER['name'],
                Role.ADMIN['name'],
                Role.DEVELOPER['name'],
            ],
        ),
):
    shop_shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shop_shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shop_shipment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    shop_shipment_method = services.shop.shipment_method.change_is_active(
        db, obj_in=shop_shipment_method, is_active=obj_in.is_active)

    schemas.shop.ShipmentMethod(
        id=shop_shipment_method.uuid,
        title=shop_shipment_method.title,
        price=shop_shipment_method.price,
        currency=shop_shipment_method.currency,
        is_active=shop_shipment_method.is_active,
    )


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_shipment_method(
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
    shop_shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shop_shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shop_shipment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    with UnitOfWork(db) as uow:
        services.shop.shipment_method.delete(uow, db_obj=shop_shipment_method)

    return


@router.get('/telegram/{shop_id}/all', response_model=List[schemas.shop.ShipmentMethod])
def get_telegram_shop_shipment_methods(
        *,
        db: Session = Depends(deps.get_db),
        shop_id: UUID4,
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    shop_shipment_methods = services.shop.shipment_method.get_multi_by_shop_id(db, shop_id=shop.id)

    return [
        schemas.shop.ShipmentMethod(
            id=shipment.uuid,
            title=shipment.title,
            price=shipment.price,
            currency=shipment.currency,
            is_active=shipment.is_active,
        )
        for shipment in shop_shipment_methods
    ]


@router.get('/telegram/{shop_id}/{shipment_id}', response_model=schemas.shop.ShipmentMethod)
def get_telegram_shop_shipment_method(
        *,
        db: Session = Depends(deps.get_db),
        shop_id: UUID4,
        shipment_id: UUID4,
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    shop_shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=shipment_id)

    if not shop_shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if not shop.id == shop_shipment_method.shop_id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    return schemas.shop.ShipmentMethod(
        id=shop_shipment_method.uuid,
        title=shop_shipment_method.title,
        price=shop_shipment_method.price,
        currency=shop_shipment_method.currency,
        is_active=shop_shipment_method.is_active,
    )

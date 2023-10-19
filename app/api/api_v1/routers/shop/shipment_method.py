from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/shipment-methods', include_in_schema=False)


@router.post('', response_model=schemas.shop.ShipmentMethod)
def create_shipment(
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

    shipment = services.shop.shipment_method.create(
        db,
        obj_in=obj_in,
        shop_id=shop.id,
    )
    return schemas.shop.ShipmentMethod(
        id=shipment.uuid,
        title=shipment.title,
        price=shipment.price,
        currency=shipment.currency,
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
    shipment = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shipment:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shipment.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    shipment = services.shop.shipment_method.update(db, db_obj=shipment, obj_in=obj_in)

    return schemas.shop.ShipmentMethod(
        id=shipment.uuid,
        title=shipment.title,
        currency=shipment.currency,
        price=shipment.price,
    )


@router.get('/{shop_id}/all', response_model=List[schemas.shop.ShipmentMethod])
def get_shipment_methods(
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

    shipment_methods = services.shop.shipment_method.get_multi_by_shop_id(db, shop_id=shop.id)

    return [
        schemas.shop.ShipmentMethod(
            id=shipment_method.uuid,
            title=shipment_method.title,
            price=shipment_method.price,
            currency=shipment_method.currency,
        )
        for shipment_method in shipment_methods
    ]


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

    shipment_method = services.shop.shipment_method.get_by_uuid(db, uuid=id)
    if not shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shipment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    services.shop.shipment_method.delete(db, db_obj=shipment_method)

    return

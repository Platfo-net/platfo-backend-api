

from typing import List

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/payment-methods')


@router.post('', response_model=schemas.shop.PaymentMethod)
def create_payment(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.PaymentMethodCreate,
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

    payment = services.shop.payment_method.create(
        db,
        obj_in=obj_in,
        shop_id=shop.id,
    )
    return schemas.shop.PaymentMethod(
        id=payment.uuid,
        title=payment.title,
        description=payment.description,
    )


@router.put('/{id}', response_model=schemas.shop.PaymentMethod)
def update_payment_method(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.PaymentMethodUpdate,
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
    payment = services.shop.payment_method.get_by_uuid(db, uuid=id)
    if not payment:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if payment.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    payment = services.shop.payment_method.update(db, db_obj=payment, obj_in=obj_in)

    return schemas.shop.PaymentMethod(
        id=payment.uuid,
        title=payment.title,
        description=payment.description,
    )


@router.get('/{shop_id}/all', response_model=List[schemas.shop.PaymentMethod])
def get_payment_methods(
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

    payment_methods = services.shop.payment_method.get_multi_by_shop_id(
        db, shop_id=shop_id)

    return [
        schemas.shop.PaymentMethod(
            id=payment_method.uuid,
            title=payment_method.title,
            description=payment_method.description,
        )
        for payment_method in payment_methods
    ]


@router.delete('/{id}', status_code=status.HTTP_200_OK)
def delete_payment_method(
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

    payment_method = services.shop.payment_method.get_by_uuid(db, uuid=id)
    if not payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if payment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    services.shop.payment_method.delete(db, db_obj=payment_method)

    return

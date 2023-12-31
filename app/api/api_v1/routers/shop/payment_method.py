from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4, ValidationError
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.payment_method import PaymentMethod
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix="/payment-methods")


@router.get("/{shop_id}/all", response_model=List[schemas.shop.PaymentMethod])
def get_shop_payment_methods(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    shop_payment_methods = services.shop.shop_payment_method.get_multi_by_shop(
        db, shop_id=shop.id
    )
    return [
        schemas.shop.PaymentMethod(
            title=payment.payment_method.title,
            description=payment.payment_method.description,
            is_active=payment.is_active,
            information_fields=payment.payment_method.information_fields,
            id=payment.uuid,
            information=payment.information,
        )
        for payment in shop_payment_methods
    ]
    items = []
    pg_items = []
    for payment in shop_payment_methods:
        if payment.payment_method.title in PaymentMethod.payment_gateway_items:
            pg_items.append(
                schemas.shop.PaymentMethod(
                    title=payment.payment_method.title,
                    description=payment.payment_method.description,
                    is_active=payment.is_active,
                    information_fields=payment.payment_method.information_fields,
                    id=payment.uuid,
                    information=payment.information,
                )
            )
        else:
            items.append(
                schemas.shop.PaymentMethod(
                    title=payment.payment_method.title,
                    description=payment.payment_method.description,
                    is_active=payment.is_active,
                    information_fields=payment.payment_method.information_fields,
                    id=payment.uuid,
                    information=payment.information,
                )
            )
    items.append(
        schemas.shop.PaymentMethod(
            title="Payment Gateway",
            description="",
            is_active=True,
            information_fields={},
            id=uuid4(),
            information={},
            items=pg_items,
        )
    )
    return items


@router.put("/{id}/change-is-active", status_code=status.HTTP_200_OK)
def change_shop_payment_method_is_active(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.shop.ChangePaymentIsActive,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    shop_payment_method = services.shop.shop_payment_method.get_by_uuid(db, uuid=id)
    if not shop_payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if shop_payment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    shop_payment_method = services.shop.shop_payment_method.change_is_active(
        db, obj_in=shop_payment_method, is_active=obj_in.is_active
    )

    return schemas.shop.PaymentMethod(
        title=shop_payment_method.payment_method.title,
        description=shop_payment_method.payment_method.description,
        is_active=shop_payment_method.is_active,
        information_fields=shop_payment_method.payment_method.information_fields,
        id=shop_payment_method.uuid,
    )


@router.put("/{id}/fill-data", response_model=schemas.shop.ShopPaymentMethod)
def payment_method_fill_information(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    obj_in: schemas.shop.EditPaymentInformation,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    shop_payment_method = services.shop.shop_payment_method.get_by_uuid(db, uuid=id)
    if not shop_payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if shop_payment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    try:
        payment_method_validation_schema = PaymentMethod.items[
            shop_payment_method.payment_method.title
        ]["validation_schema"]
        payment_method_validation_schema(**obj_in.information)
    except ValidationError:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_INFORMATION_INVALID)

    shop_payment_method = services.shop.shop_payment_method.edit_information(
        db, obj_in=shop_payment_method, information=obj_in.information
    )

    return schemas.shop.ShopPaymentMethod(
        title=shop_payment_method.payment_method.title,
        description=shop_payment_method.payment_method.description,
        is_active=shop_payment_method.is_active,
        information=shop_payment_method.information,
        id=shop_payment_method.uuid,
    )


@router.get("/{id}", response_model=schemas.shop.ShopPaymentMethod)
def get_payment_method(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER["name"],
            Role.ADMIN["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    shop_payment_method = services.shop.shop_payment_method.get_by_uuid(db, uuid=id)
    if not shop_payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if shop_payment_method.shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    return schemas.shop.ShopPaymentMethod(
        title=shop_payment_method.payment_method.title,
        description=shop_payment_method.payment_method.description,
        is_active=shop_payment_method.is_active,
        information=shop_payment_method.information,
        id=shop_payment_method.uuid,
    )


@router.get("/telegram/{shop_id}/all", response_model=List[schemas.shop.PaymentMethod])
def get_shop_payment_methods_for_telegram_shop(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    shop_payment_methods = services.shop.shop_payment_method.get_multi_by_shop(
        db, shop_id=shop.id, is_active=True
    )
    return [
        schemas.shop.PaymentMethod(
            title=payment.payment_method.title,
            description=payment.payment_method.description,
            is_active=payment.is_active,
            information_fields=payment.payment_method.information_fields,
            id=payment.uuid,
            information=payment.information,
        )
        for payment in shop_payment_methods
    ]
    items = []
    pg_items = []
    for payment in shop_payment_methods:
        if payment.payment_method.title in PaymentMethod.payment_gateway_items:
            pg_items.append(
                schemas.shop.PaymentMethod(
                    title=payment.payment_method.title,
                    description=payment.payment_method.description,
                    is_active=payment.is_active,
                    information_fields=payment.payment_method.information_fields,
                    id=payment.uuid,
                    information=payment.information,
                )
            )
        else:
            items.append(
                schemas.shop.PaymentMethod(
                    title=payment.payment_method.title,
                    description=payment.payment_method.description,
                    is_active=payment.is_active,
                    information_fields=payment.payment_method.information_fields,
                    id=payment.uuid,
                    information=payment.information,
                )
            )
    items.append(
        schemas.shop.PaymentMethod(
            title="Payment Gateway",
            description="",
            is_active=True,
            information_fields={},
            id=uuid4(),
            information={},
            items=pg_items,
        )
    )
    return items

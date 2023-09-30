from datetime import datetime
from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/credit')


@router.get('/shop/{shop_id}', response_model=schemas.credit.Invoice)
def get_shop_credit(
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

    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop.id)
    if not credit:
        raise_http_exception(Error.SHOP_CREDIT_NOT_FOUND)

    return schemas.credit.ShopCredit(
        expires_at=credit.expires_at,
        is_expired=credit.expires_at < datetime.now()
    )


@router.put('/shop/{shop_id}/add-credit', status_code=status.HTTP_200_OK)
def add_days_to_shop_credit(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    obj_in: schemas.credit.AddDaysCredit,
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

    credit = services.credit.shop_credit.get_by_shop_id(db, shop_id=shop.id)
    if not credit:
        raise_http_exception(Error.SHOP_CREDIT_NOT_FOUND)

    new_credit = services.credit.shop_credit.add_shop_credit(
        db, db_obj=credit, days=obj_in.days_added)

    return schemas.credit.ShopCredit(
        expires_at=new_credit.expires_at,
        is_expired=new_credit.expires_at < datetime.now()
    )

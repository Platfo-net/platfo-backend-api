from datetime import datetime

from app.core.telegram import tasks
from fastapi import APIRouter, Depends, Security, status
from pydantic import UUID4
from sqlalchemy.orm import Session
from suds.client import Client

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.constants.shop_telegram_payment_status import \
    ShopTelegramPaymentRecordStatus
from app.core.config import settings
from app.core.exception import raise_http_exception
from app.core.unit_of_work import UnitOfWork

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


@router.get('/shop/telegram/{telegram_shop_payment_record_id}/verify',
            status_code=status.HTTP_200_OK)
def verify_telegram_shop_payment_record(
    *,
    db: Session = Depends(deps.get_db),
    telegram_shop_payment_record_id: int,
):
    shop_telegram_payment_record = services.credit.shop_telegram_payment_record.get(
        db, id=telegram_shop_payment_record_id)
    if not shop_telegram_payment_record:
        raise_http_exception(Error.SHOP_TELEGRAM_PAYMENT_RECORD_NOT_FOUND)

    if shop_telegram_payment_record.status == ShopTelegramPaymentRecordStatus.APPLIED:
        raise_http_exception(Error.SHOP_TELEGRAM_PAYMENT_HAS_BEEN_ALREADY_APPLIED)

    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    result = zarrin_client.service.PaymentVerification(
        settings.ZARINPAL_MERCHANT_ID,
        shop_telegram_payment_record.payment_authority,
        shop_telegram_payment_record.amount,
    )

    if result.Status not in [100, 101]:
        raise_http_exception(Error.SHOP_TELEGRAM_PAYMENT_FAILED)

    shop_credit = services.credit.shop_credit.get_by_shop_id(
        db, shop_id=shop_telegram_payment_record.shop_id)

    if not shop_credit:
        raise_http_exception(Error.SHOP_CREDIT_NOT_FOUND)

    with UnitOfWork(db) as uow:
        services.credit.shop_credit.add_shop_credit(
            uow, db_obj=shop_credit, days=shop_telegram_payment_record.plan.extend_days
        )

        shop_telegram_payment_record = services.credit.shop_telegram_payment_record.change_status(
            uow,
            db_obj=shop_telegram_payment_record,
            status=ShopTelegramPaymentRecordStatus.APPLIED
        )

        services.credit.shop_telegram_payment_record.add_ref_id(
            uow, db_obj=shop_telegram_payment_record, ref_id=result.RefID
        )

    tasks.send_credit_extending_successful_notification_task.delay(
        shop_credit_id=shop_credit.id,
        shop_telegram_payment_record_id=shop_telegram_payment_record.id)

    return "پرداخت با موفقیت انجام شد."

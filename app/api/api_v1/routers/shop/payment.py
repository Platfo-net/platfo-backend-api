from fastapi import status
from app.constants.payment_method import PaymentMethod
from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.currency import Currency
from app.constants.errors import Error
from app.constants.order_status import OrderStatus
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.exception import raise_http_exception
from app.core.telegram import tasks as telegram_tasks
from app.core.unit_of_work import UnitOfWork
from suds.client import Client

router = APIRouter(prefix='/payment')


@router.get("/order/{order_id}")
def get_order_payment_link(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return "order not found"
    order_total_amount = 0

    for item in order.items:
        order_total_amount += item.price * item.count

    shop_zarin_info = services.shop.shop_payment_method.get(
        db, id=order.shop_payment_method_id).information["merchant_id"]

    zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
    callback = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/shop/payment/zarin-pal/{order.uuid}/verify"  # noqa
    result = zarrin_client.service.PaymentRequest(
        shop_zarin_info,
        order_total_amount,
        f"پرداخت بابت سفارش شماره {order.order_number}",
        "",
        "",
        callback,
    )

    return f"{settings.ZARINPAL_BASE_URL}/{result.Authority}"


@router.get("/zarin-pal/{order_id}/verify", status_code=status.HTTP_200_OK)
def verify_order_payment(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
):
    print(order_id)
    return "OOOK"

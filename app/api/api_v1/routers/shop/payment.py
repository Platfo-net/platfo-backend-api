from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from pydantic import UUID4
from sqlalchemy.orm import Session
from suds.client import Client

from app import services
from app.api import deps
from app.constants.payment_method import PaymentMethod
from app.core.config import settings

router = APIRouter(prefix='/payment')


@router.get("/order/{order_id}", response_class=RedirectResponse)
def get_order_payment_link(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        return "order not found"

    if order.shop_payment_method.payment_method.title not in [PaymentMethod.ZARRIN_PAL["title"]]:
        return "Payment is not online"

    order_total_amount = 0

    for item in order.items:
        order_total_amount += item.price * item.count
    if order.shipment_method:
        order_total_amount += order.shipment_method.price

    payment_method_info = services.shop.shop_payment_method.get(
        db, id=order.shop_payment_method_id).information

    if order.shop_payment_method.payment_method.title == PaymentMethod.ZARRIN_PAL["title"]:
        zarrin_pal_merchant_id = payment_method_info.get("merchant_id")
        if not zarrin_pal_merchant_id:
            return "Invalid payment info"

        zarrin_client = Client(settings.ZARINPAL_WEBSERVICE)
        callback = f"{settings.SERVER_ADDRESS_NAME}{settings.API_V1_STR}/shop/payment/zarin-pal/{order.uuid}/verify"  # noqa
        result = zarrin_client.service.PaymentRequest(
            zarrin_pal_merchant_id,
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

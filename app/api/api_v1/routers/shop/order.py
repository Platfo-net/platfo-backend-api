from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.order_status import OrderStatus
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.core.telegram import tasks as telegram_tasks
from app.core.unit_of_work import UnitOfWork

router = APIRouter(prefix='/orders/telegram')


@router.post("/{shop_id}/{lead_id}", response_model=schemas.shop.OrderCreateResponse)
def create_telegram_shop_order(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.shop.OrderCreate,
    shop_id: UUID4,
    lead_id: UUID4,
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)

    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    lead = services.social.telegram_lead.get_by_uuid(db, uuid=lead_id)
    if not lead:
        raise_http_exception(Error.LEAD_TELEGRAM_LEAD_NOT_FOUND)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(db, shop_id=shop.id)
    if lead.telegram_bot_id != shop_telegram_bot.telegram_bot_id:
        raise_http_exception(Error.LEAD_TELEGRAM_LEAD_NOT_FOUND_ACCESS_DENIED)

    shop_payment_method = services.shop.shop_payment_method.get_by_uuid(
        db, uuid=obj_in.payment_method_id)
    if not shop_payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)
    if shop_payment_method.shop_id != shop.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    with UnitOfWork(db)as uow:
        order_items = []
        for item in obj_in.items:
            product = services.shop.product.get_by_uuid(db, uuid=item.product_id)
            if not product or product.shop_id != shop.id:
                raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR)
            order_items.append(schemas.shop.OrderItemCreate(
                product_id=product.id,
                count=item.count,
                price=product.price,
                currency=product.currency,
            ))
        last_order_number = services.shop.order.get_last_order_number(db, shop_id=shop.id)

        order = services.shop.order.create(
            uow,
            obj_in=obj_in,
            shop_id=shop.id,
            lead_id=lead.id,
            shop_payment_method_id=shop_payment_method.id,
            order_number=last_order_number + 1,
            status=OrderStatus.UNPAID["value"],
        )

        services.shop.order_item.create_bulk(uow, objs_in=order_items, order_id=order.id)

        telegram_order = services.shop.telegram_order.create(uow, order_id=order.id)

        telegram_tasks.send_lead_order_to_bot_and_support_bot_task.delay(
            shop_telegram_bot.telegram_bot.id, lead.id, order.id, telegram_order.id, "fa")

        return schemas.shop.order.OrderCreateResponse(
            order_number=str(order.order_number)
        )


@router.get("/{order_id}", response_model=schemas.shop.OrderSummary)
def get_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.SHOP['name'],
            Role.ADMIN['name'],
        ],
    ),
):

    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        raise_http_exception(Error.SHOP_ORDER_NOT_FOUND)

    sum = 0
    for item in order.items:
        sum += item.product.price * item.count

    return schemas.shop.OrderSummary(
        first_name=order.first_name,
        last_name=order.last_name,
        phone_number=order.phone_number,
        order_number=order.order_number,
        total_amount=sum
    )

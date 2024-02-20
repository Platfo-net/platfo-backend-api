from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.currency import Currency
from app.constants.errors import Error
from app.constants.order_status import OrderStatus
from app.constants.payment_method import PaymentMethod
from app.constants.role import Role
from app.core import storage
from app.core.config import settings
from app.core.exception import raise_http_exception
from app.core.telegram import tasks as telegram_tasks
from app.core.unit_of_work import UnitOfWork

router = APIRouter(prefix="/orders", tags=["Shop Order"])


@router.post(
    "/telegram/{shop_id}/{lead_id}", response_model=schemas.shop.OrderCreateResponse
)
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
    # if not lead:
    #     raise_http_exception(Error.LEAD_TELEGRAM_LEAD_NOT_FOUND)

    shop_telegram_bot = services.shop.shop_telegram_bot.get_by_shop_id(
        db, shop_id=shop.id
    )
    # if lead.telegram_bot_id != shop_telegram_bot.telegram_bot_id:
    #     raise_http_exception(Error.LEAD_TELEGRAM_LEAD_NOT_FOUND_ACCESS_DENIED)

    shop_payment_method = services.shop.shop_payment_method.get_by_uuid(
        db, uuid=obj_in.payment_method_id
    )
    if not shop_payment_method:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR)

    if shop_payment_method.shop_id != shop.id:
        raise_http_exception(Error.SHOP_PAYMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    shipment_method = services.shop.shipment_method.get_by_uuid(
        db, uuid=obj_in.shipment_method_id
    )
    if not shipment_method:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR)

    if shipment_method.shop_id != shop.id:
        raise_http_exception(Error.SHOP_SHIPMENT_METHOD_NOT_FOUND_ERROR_ACCESS_DENIED)

    table = None
    if obj_in.table_id:
        table = services.shop.table.get_by_uuid(db, uuid=obj_in.table_id)

    with UnitOfWork(db) as uow:
        order_items = []
        last_order_number = services.shop.order.get_last_order_number(
            db, shop_id=shop.id
        )

        order = services.shop.order.create(
            uow,
            obj_in=obj_in,
            shop_id=shop.id,
            lead_id=lead.id if lead else None,
            shop_payment_method_id=shop_payment_method.id,
            shipment_method_id=shipment_method.id,
            order_number=last_order_number + 1,
            status=OrderStatus.UNPAID["value"],
            table_id=table if not table else table.id,
        )

    with UnitOfWork(db) as uow:
        for item in obj_in.items:
            product = services.shop.product.get_by_uuid(db, uuid=item.product_id)
            if not product or product.shop_id != shop.id:
                raise_http_exception(Error.SHOP_PRODUCT_NOT_FOUND_ERROR)

            variant = services.shop.product_variant.get_by_uuid(db, uuid=item.variant_id)
            if variant:
                if not variant.is_available:
                    raise_http_exception(Error.SHOP_PRODUCT_VARIANT_NOT_FOUND_ERROR)

                price = variant.price
                currency = variant.currency
                variant_title = variant.title
            else:
                price = product.price
                currency = product.currency
                variant_title = None

            order_items.append(
                schemas.shop.OrderItem(
                    product_id=product.id,
                    count=item.count,
                    price=price,
                    currency=currency,
                    product_title=product.title,
                    variant_title=variant_title,
                )
            )
        services.shop.order_item.create_bulk(
            uow, objs_in=order_items, order_id=order.id
        )
        telegram_order = services.shop.telegram_order.create(uow, order_id=order.id)

    telegram_tasks.send_lead_order_to_bot_and_support_bot_task.delay(
        shop_telegram_bot.telegram_bot.id,
        lead.id if lead else None,
        order.id,
        telegram_order.id,
        "fa",
    )

    return schemas.shop.order.OrderCreateResponse(order_number=str(order.order_number))


@router.get("/{shop_id}/all", response_model=schemas.shop.OrderListApiResponse)
def get_orders_by_shop_id(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: UUID4,
    page: int = 1,
    page_size: int = 20,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    shop = services.shop.shop.get_by_uuid(db, uuid=shop_id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if not shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    orders, pagination = services.shop.order.get_multi_by_shop_id(
        db, shop_id=shop.id, page=page, page_size=page_size
    )
    orders_list = []
    for order in orders:
        sum = 0
        for item in order.items:
            sum += item.price * item.count

        table = None
        if order.table_id:
            table = schemas.shop.Table(
                id=order.table.uuid,
                title=order.table.title,
            )

        orders_list.append(
            schemas.shop.OrderListItem(
                id=order.uuid,
                order_number=order.order_number,
                first_name=order.first_name,
                last_name=order.last_name,
                phone_number=order.phone_number,
                city=order.city,
                total_amount=sum,
                currency=Currency.IRT["name"],
                created_at=order.created_at,
                payment_method=PaymentMethod.items[
                    order.shop_payment_method.payment_method.title
                ]["fa"]
                if order.shop_payment_method
                else "",  # noqa
                shipment_method=order.shipment_method.title
                if order.shipment_method
                else "",
                status=OrderStatus.items[order.status]["title"]["fa"],
                table=table
            )
        )

    return schemas.shop.OrderListApiResponse(
        items=orders_list,
        pagination=pagination,
    )


@router.get("/{order_id}", response_model=schemas.shop.Order)
def get_order(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        raise_http_exception(Error.SHOP_ORDER_NOT_FOUND)

    if not order.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_ORDER_NOT_FOUND_ACCESS_DENIED)

    sum = 0
    items = []

    table = None
    if order.table_id:
        table = schemas.shop.Table(
            id=order.table.uuid,
            title=order.table.title,
        )
    for item in order.items:
        sum += item.price * item.count
        image_url = storage.get_object_url(
            item.product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET
        )
        product_title = item.product_title if item.product_title else item.product.title
        items.append(
            schemas.shop.OrderItemResponse(
                count=item.count,
                price=item.price,
                currency=item.currency,
                product_title=product_title,
                variant_title=item.variant_title,
                image=image_url,
            )
        )

    return schemas.shop.Order(
        id=order.uuid,
        first_name=order.first_name,
        last_name=order.last_name,
        phone_number=order.phone_number,
        email=order.email,
        order_number=order.order_number,
        total_amount=sum,
        currency=Currency.IRT["name"],
        address=order.address,
        state=order.state,
        city=order.city,
        items=items,
        payment_method=PaymentMethod.items[
            order.shop_payment_method.payment_method.title
        ]["fa"]
        if order.shop_payment_method
        else "",  # noqa
        shipment_method=order.shipment_method.title if order.shipment_method else "",
        status=OrderStatus.items[order.status]["title"]["fa"],
        payment_information=order.payment_information,
        table=table
    )


@router.put("/{order_id}/change-status", response_model=schemas.shop.Order)
def change_order_status(
    *,
    db: Session = Depends(deps.get_db),
    order_id: UUID4,
    obj_in: schemas.shop.OrderChangeStatus,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN["name"],
            Role.USER["name"],
            Role.DEVELOPER["name"],
        ],
    ),
):
    order = services.shop.order.get_by_uuid(db, uuid=order_id)
    if not order:
        raise_http_exception(Error.SHOP_ORDER_NOT_FOUND)

    if not order.shop.user_id == current_user.id:
        raise_http_exception(Error.SHOP_ORDER_NOT_FOUND_ACCESS_DENIED)

    if not OrderStatus.items.get(obj_in.status):
        raise_http_exception(Error.SHOP_INVALID_ORDER_STATUS)

    order = services.shop.order.change_status(db, order=order, status=obj_in.status)

    sum = 0
    items = []

    table = None
    if order.table_id:
        table = schemas.shop.Table(
            id=order.table.uuid,
            title=order.table.title,
        )
    for item in order.items:
        product_title = item.product_title if item.product_title else item.product.title

        sum += item.price * item.count
        image_url = storage.get_object_url(
            item.product.image, settings.S3_SHOP_PRODUCT_IMAGE_BUCKET
        )
        items.append(
            schemas.shop.OrderItemResponse(
                count=item.count,
                price=item.price,
                currency=item.currency,
                product_title=product_title,
                variant_title=item.variant_title,
                image=image_url,
            )
        )

    telegram_tasks.order_change_status_from_dashboard_task.delay(order.id, "fa")

    return schemas.shop.Order(
        id=order.uuid,
        first_name=order.first_name,
        last_name=order.last_name,
        phone_number=order.phone_number,
        email=order.email,
        order_number=order.order_number,
        total_amount=sum,
        currency=Currency.IRT["name"],
        address=order.address,
        state=order.state,
        city=order.city,
        items=items,
        payment_method=PaymentMethod.items[
            order.shop_payment_method.payment_method.title
        ]["fa"]
        if order.shop_payment_method
        else "",  # noqa
        shipment_method=order.shipment_method.title if order.shipment_method else "",
        status=OrderStatus.items[order.status]["title"]["fa"],
        payment_information=order.payment_information,
        table=table,

    )

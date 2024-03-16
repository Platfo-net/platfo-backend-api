from datetime import timedelta

from pydantic import UUID4

from app.core.utils import get_today_datetime_range
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/dashboard', tags=["Shop Dashboard"])


@router.post('/{shop_id}/daily', response_model=schemas.shop.ShopDailyDashboard)
def get_daily_report(
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

    today_start, tomorrow_start = get_today_datetime_range()

    today_orders = services.shop.order.get_orders_by_datetime(
        db, shop_id=shop.id, from_datetime=today_start, to_datetime=tomorrow_start)

    today_orders_count = len(today_orders)
    today_orders_sum = 0
    for order in today_orders:
        today_orders_sum += order.total_amount

    today_orders_average = 0
    if today_orders_count:
        today_orders_average = today_orders_sum / today_orders_count

    return schemas.shop.ShopDailyDashboard(
        today_orders_count=today_orders_count,
        today_orders_sum=today_orders_sum,
        today_orders_average=today_orders_average,
    )


@router.post('/{shop_id}/monthly', response_model=schemas.shop.ShopMonthlyDashboard)
def get_last_month_report(
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

    today_start, _ = get_today_datetime_range()

    last_30_days_reports = services.shop.daily_report.get_datetime_range_reports(
        db,
        shop_id=shop.id,
        from_date=today_start.date() - timedelta(days=30),
        to_date=today_start.date(),
    )

    last_30_days = {}
    for _ in range(30):
        today_start -= timedelta(days=1)
        last_30_days[today_start.date()] = {
            "count": 0,
            "amount": 0,
            "avg": 0,
        }

    for report in last_30_days_reports:
        last_30_days[report.date]["count"] = report.order_count
        last_30_days[report.date]["amount"] = report.order_amount
        if report.order_count:
            last_30_days[report.date]["avg"] = report.order_amount / report.order_count

    orders_amount = []
    orders_count = []
    orders_average = []

    for key, value in last_30_days.items():
        orders_amount.append(
            schemas.shop.ShopMonthlyDashboardItem(
                date=key,
                value=value["amount"]
            )
        )
        orders_count.append(
            schemas.shop.ShopMonthlyDashboardItem(
                date=key,
                value=value["count"]
            )
        )
        orders_average.append(
            schemas.shop.ShopMonthlyDashboardItem(
                date=key,
                value=value["avg"]
            )
        )

    return schemas.shop.ShopMonthlyDashboard(
        orders_amount=orders_amount,
        orders_count=orders_count,
        orders_average=orders_average
    )

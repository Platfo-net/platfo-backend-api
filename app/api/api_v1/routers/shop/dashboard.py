from datetime import timedelta

from fastapi import APIRouter, Depends, Security
from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception
from app.core.telegram import helpers
from app.core.utils import get_today_datetime_range

router = APIRouter(prefix='/dashboard', tags=["Shop Dashboard"])


def get_today_report(db: Session, shop_id, today_start, tomorrow_start):
    today_orders = services.shop.order.get_orders_by_datetime(
        db, shop_id=shop_id, from_datetime=today_start, to_datetime=tomorrow_start)

    today_orders_count = len(today_orders)
    today_orders_sum = 0
    for order in today_orders:
        today_orders_sum += order.total_amount

    return today_orders_count, today_orders_sum


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

    today_start, tomorrow_start = get_today_datetime_range()

    today_count, today_amount = get_today_report(db, shop.id, today_start, tomorrow_start)

    last_30_days_reports = services.shop.daily_report.get_datetime_range_reports(
        db,
        shop_id=shop.id,
        from_date=today_start.date() - timedelta(days=29),
        to_date=today_start.date(),
    )

    last_30_days = {
        today_start.date(): {
            "count": today_count,
            "amount": today_amount,
            "avg": 0 if not today_count else today_amount / today_count,
        }
    }
    for _ in range(29):
        today_start -= timedelta(days=1)
        last_30_days[today_start.date()] = {
            "count": 0,
            "amount": 0,
            "avg": 0,
        }

    total_orders_count = today_count
    total_orders_amount = today_amount

    for report in last_30_days_reports:
        last_30_days[report.date]["count"] = report.order_count
        last_30_days[report.date]["amount"] = report.order_amount
        if report.order_count:
            last_30_days[report.date]["avg"] = report.order_amount / report.order_count

        total_orders_amount += report.order_amount
        total_orders_count += report.order_count

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

    orders_total_average = 0
    if total_orders_count:
        orders_total_average = total_orders_amount / total_orders_count
    return schemas.shop.ShopMonthlyDashboard(
        orders_count_per_day=reversed(orders_count),
        orders_amount_per_day=reversed(orders_amount),
        orders_average_per_day=reversed(orders_average),
        orders_total_amount=helpers.number_to_price(int(total_orders_amount)),
        orders_total_count=total_orders_count,
        orders_total_average=helpers.number_to_price(int(orders_total_average))
    )

from datetime import timedelta

from core.utils import get_today_datetime_range
from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from app.core.exception import raise_http_exception

router = APIRouter(prefix='/dashboard', tags=["Shop Dashboard"])


@router.post('/{shop_id}', response_model=schemas.shop.GeneralShopDashboard)
def get_dashboard(
    *,
    db: Session = Depends(deps.get_db),
    shop_id: int,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.USER['name'],
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
):

    shop = services.shop.shop.get_by_uuid(db, uuid=id)
    if not shop:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ERROR)

    if shop.user_id != current_user.id:
        raise_http_exception(Error.SHOP_SHOP_NOT_FOUND_ACCESS_DENIED_ERROR)

    today_start, tomorrow_start = get_today_datetime_range()

    last_30_days_reports = services.shop.daily_report.get_datetime_range_reports(
        db,
        shop_id=shop.id,
        from_date=today_start.date() - timedelta(days=30),
        to_date=today_start.date(),
    )

    today_orders = services.shop.order.get_orders_by_datetime(
        db, shop_id=shop_id, from_datetime=today_start, to_datetime=tomorrow_start)

    last_30_days_orders_count = 0
    last_30_days_orders_sum = 0
    for report in last_30_days_reports:
        last_30_days_orders_sum += report.order_amount
        last_30_days_orders_sum += report.order_count

    today_orders_count = len(today_orders)
    today_orders_sum = 0
    for order in today_orders:
        today_orders_sum += order.total_amount

    last_30_days_orders_average = 0
    if (last_30_days_orders_count + today_orders_count):
        last_30_days_orders_average = (
            (last_30_days_orders_sum + today_orders_sum) /  # noqa
            (last_30_days_orders_count + today_orders_count)  # noqa
        )
    today_orders_average = 0
    if today_orders_count:
        today_orders_average = today_orders_sum / today_orders_count

    return schemas.shop.GeneralShopDashboard(
        last_30_days_orders_count=last_30_days_orders_count + today_orders_count,
        last_30_days_orders_sum=last_30_days_orders_sum + today_orders_sum,
        today_orders_count=today_orders_count,
        today_orders_sum=today_orders_sum,
        last_30_days_orders_average=last_30_days_orders_average,
        today_orders_average=today_orders_average,
    )

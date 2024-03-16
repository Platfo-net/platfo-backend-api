

from typing import Optional

from pydantic import BaseModel


class GeneralShopDashboard(BaseModel):
    last_30_days_orders_count: Optional[int] = 0
    last_30_days_orders_sum: Optional[float] = 0.0
    today_orders_count: Optional[int] = 0
    today_orders_sum: Optional[float] = 0.0
    last_30_days_orders_average: Optional[float] = 0.0
    today_orders_average: Optional[float] = 0.0

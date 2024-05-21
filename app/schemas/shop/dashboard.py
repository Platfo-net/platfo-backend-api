

from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel


class ShopDailyDashboard(BaseModel):
    today_orders_count: Optional[int] = 0
    today_orders_sum: Optional[float] = 0.0
    today_orders_average: Optional[float] = 0.0


class ShopMonthlyDashboardItem(BaseModel):
    date: date
    value: Union[int, float]


class ShopMonthlyDashboard(BaseModel):
    orders_count_per_day: List[ShopMonthlyDashboardItem]
    orders_amount_per_day: List[ShopMonthlyDashboardItem]
    orders_average_per_day: List[ShopMonthlyDashboardItem]

    orders_total_count: Optional[int] = 0
    orders_total_amount: Optional[str] = "0"
    orders_total_average: Optional[str] = "0"

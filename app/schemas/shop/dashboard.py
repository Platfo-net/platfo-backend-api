

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
    orders_count: List[ShopMonthlyDashboardItem]
    orders_amount: List[ShopMonthlyDashboardItem]
    orders_average: List[ShopMonthlyDashboardItem]

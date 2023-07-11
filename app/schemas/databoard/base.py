

from pydantic import BaseModel


class DailyStat(BaseModel):
    year: int
    month: int
    day: int
    count: int


class HourlyStat(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    count: int


class MonthlyStat(BaseModel):
    year: int
    month: int
    count: int

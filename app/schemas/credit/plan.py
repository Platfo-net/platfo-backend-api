from typing import List

from pydantic import UUID4, BaseModel


class Feature(BaseModel):
    id: UUID4
    title: str = None
    description: str = None


class Plan(BaseModel):
    id: UUID4
    title: str = None
    description: str = None
    is_active: bool = True
    extend_days: int = None
    extend_count: int = None

    original_price: float = None
    discounted_price: float = None
    currency: str = None
    discount_percentage: float = None
    is_discounted: bool = False

    module: str = None


class DetailedPlan(Plan):
    features: List[Feature]

    class Config:
        orm_mode = True

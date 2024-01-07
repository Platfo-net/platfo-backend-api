from typing import List, Optional

from pydantic import UUID4, BaseModel


class Feature(BaseModel):
    id: UUID4
    title: str = None
    description: str = None


class Plan(BaseModel):
    id: UUID4
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    extend_days: Optional[int] = None
    extend_count: Optional[int] = None

    original_price: Optional[float] = None
    discounted_price: Optional[float] = None
    currency: Optional[str] = None
    discount_percentage: Optional[float] = None

    module: str = None


class DetailedPlan(Plan):
    features: List[Feature]

    class Config:
        from_attributes = True

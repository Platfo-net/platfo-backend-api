

from typing import List
from pydantic import UUID4, BaseModel


class PlanCreate(BaseModel):
    title: str = None
    description: str = None
    is_active: bool = True
    extend_days: int = 0
    extend_count: int = 0
    module = str


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
    module = str
    features: List[Feature]

    class Config:
        orm_mode = True

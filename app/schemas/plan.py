from typing import Optional

from pydantic import UUID4, BaseModel


class PlanBase(BaseModel):
    price: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    days_add: Optional[int] = True


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanInDBBase(PlanBase):
    id: UUID4

    class Config:
        orm_mode = True


class Plan(PlanInDBBase):
    pass


class PlanInDB(PlanInDBBase):
    pass

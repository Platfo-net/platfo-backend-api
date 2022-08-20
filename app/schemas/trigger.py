from typing import Optional

from pydantic import UUID4, BaseModel


class TriggerBase(BaseModel):
    name: Optional[str] = None
    persian_name: Optional[str] = None
    platform: Optional[str] = None


class TriggerCreate(TriggerBase):
    pass


class TriggerUpdate(TriggerBase):
    pass


class TriggerInDBBase(TriggerBase):
    id: UUID4

    class Config:
        orm_mode = True


class Trigger(TriggerInDBBase):
    pass


class TriggerInDB(TriggerInDBBase):
    pass

from typing import Optional

from pydantic import BaseModel


class AttributeBase(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(AttributeBase):
    pass


class Attribute(AttributeBase):
    pass

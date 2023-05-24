from typing import Optional

from pydantic import UUID4, BaseModel


class RoleBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    persian_name: Optional[str]


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    id: UUID4

    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    pass


class RoleInDB(RoleInDBBase):
    pass

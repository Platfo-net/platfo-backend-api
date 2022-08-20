from datetime import datetime
from typing import Optional

from app.schemas.role import Role
from pydantic import UUID4, BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: Optional[UUID4] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(UserBase):
    pass


class UserUpdatePassword(BaseModel):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: UUID4
    role: Optional[Role]

    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserInDB(UserInDBBase):
    hashed_password: str


class ForgetPassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str

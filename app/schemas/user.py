from datetime import datetime
from typing import Optional , Any

from app.schemas.role import Role
from pydantic import UUID4, BaseModel, EmailStr, Field, root_validator


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: Optional[str] = None
    role_id: int


class UserUpdate(UserBase):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdatePassword(BaseModel):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id : Any
    created_at: datetime
    updated_at: datetime
    role : Optional[Role]
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
    password: str

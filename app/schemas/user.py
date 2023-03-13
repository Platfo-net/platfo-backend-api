from datetime import datetime
from typing import Optional

from app.schemas.role import Role
from .media import Image
from pydantic import UUID4, BaseModel, EmailStr


class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    phone_number: Optional[str] = None
    phone_country_code: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: Optional[str] = None
    role_id: int
    is_email_verified: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_image: Optional[str] = None


class UserUpdatePassword(BaseModel):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    role: Optional[Role]

    class Config:
        orm_mode = True


class User(UserInDBBase):
    profile_image: Optional[Image] = None


class UserRegister(BaseModel):
    phone_number: str
    phone_country_code: str
    password: str


class UserInDB(UserInDBBase):
    hashed_password: str


class ForgetPassword(BaseModel):
    email: EmailStr


class ChangePassword(BaseModel):
    email: EmailStr
    code: int
    password: str
    token: str


class RegisterCode(BaseModel):
    token: str


class ActivationData(BaseModel):
    code: int
    token: str
    email: EmailStr

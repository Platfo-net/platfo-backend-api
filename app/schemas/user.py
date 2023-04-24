from datetime import datetime
from typing import Optional
from app.core import utils

from app.schemas.role import Role
from .media import Image
from pydantic import UUID4, BaseModel, EmailStr, validator


class PhoneValidator(BaseModel):
    phone_number: str
    phone_country_code: str

    @validator("phone_number", always=True)
    def validate_phone_number(cls, phone_number, values):
        return utils.normalize_phone_number(phone_number)

    @validator("phone_country_code", always=True)
    def validate_phone_country_code(cls, phone_country_code, values):
        return utils.normalize_phone_country_code(phone_country_code)


class PhoneData(PhoneValidator):
    pass


class UserBase(PhoneValidator):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
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


class UserRegister(PhoneValidator):
    email: Optional[EmailStr] = None
    password: str


class UserRegisterByPhoneNumber(PhoneValidator):
    password: str


class UserRegisterByEmail(BaseModel):
    email: EmailStr
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


class ActivationDataByPhoneNumber(PhoneValidator):
    code: int
    token: str


class ActivationDataByEmail(BaseModel):
    code: int
    token: str
    email: EmailStr

from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, EmailStr, validator

from app.schemas.role import Role

from .media import Image


def normalize_phone_number(phone_number):
    if not phone_number:
        return phone_number
    if phone_number[0] == "0":
        phone_number = phone_number[1:]
    return phone_number


def get_full_phone_number(phone_number, phone_country_code):
    return "{}{}".format(
        normalize_phone_number(phone_number),
        normalize_phone_country_code(phone_country_code),
    )


def normalize_phone_country_code(phone_country_code):
    if not phone_country_code:
        return phone_country_code

    new_phone_country_code = phone_country_code
    if phone_country_code[0:2] == "00":
        new_phone_country_code = phone_country_code[2:]
    if phone_country_code[0] == "+":
        new_phone_country_code = phone_country_code[1:]
    return new_phone_country_code


class PhoneValidator(BaseModel):
    phone_number: str
    phone_country_code: str

    @validator("phone_number", always=True)
    def validate_phone_number(cls, phone_number, values):
        return normalize_phone_number(phone_number)

    @validator("phone_country_code", always=True)
    def validate_phone_country_code(cls, phone_country_code, values):
        return normalize_phone_country_code(phone_country_code)


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
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class UserRegisterByPhoneNumber(PhoneValidator):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str


class UserRegisterByEmail(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
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

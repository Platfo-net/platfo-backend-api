from pydantic import BaseModel, validator

from app.schemas.role import Role


def normalize_phone_country_code(phone_country_code):
    if not phone_country_code:
        return phone_country_code

    new_phone_country_code = phone_country_code
    if phone_country_code[0:2] == '00':
        new_phone_country_code = phone_country_code[2:]
    if phone_country_code[0] == '+':
        new_phone_country_code = phone_country_code[1:]
    return new_phone_country_code


def normalize_phone_number(phone_number):
    if not phone_number:
        return phone_number
    if phone_number[0] == '0':
        phone_number = phone_number[1:]
    return phone_number


class Token(BaseModel):
    access_token: str
    token_type: str


class Login(BaseModel):
    access_token: str
    token_type: str
    role: Role

    class Config:
        orm_mode = True


class TokenPayload(BaseModel):
    id: int
    role: str = None


class LoginFormByEmail(BaseModel):
    email: str
    password: str


class LoginFormByPhoneNumber(BaseModel):
    phone_number: str
    phone_country_code: str
    password: str

    @validator('phone_number', always=True)
    def validate_phone_number(cls, phone_number, values):
        return normalize_phone_number(phone_number)

    @validator('phone_country_code', always=True)
    def validate_phone_country_code(cls, phone_country_code, values):
        return normalize_phone_country_code(phone_country_code)

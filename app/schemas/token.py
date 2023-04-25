from pydantic import BaseModel, validator
from app.schemas.role import Role


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

    @validator("phone_number", always=True)
    def validate_phone_number(cls, phone_number, values):
        pass
        # return utils.normalize_phone_number(phone_number)

    @validator("phone_country_code", always=True)
    def validate_phone_country_code(cls, phone_country_code, values):
        pass
        # return utils.normalize_phone_country_code(phone_country_code)

from pydantic import UUID4, BaseModel
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
    uuid: UUID4
    role: str = None


class LoginFormByEmail(BaseModel):
    email: str
    password: str


class LoginFormByPhoneNumber(BaseModel):
    phone_number: str
    phone_country_code: str
    password: str

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
    id: UUID4
    role: str = None


class LoginForm(BaseModel):
    email: str
    password: str

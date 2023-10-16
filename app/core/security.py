from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

ALGORITHM = 'HS256'


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {'exp': expire, **subject}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(db: Session, *, user: models.User):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if not user.role:
        role = 'GUEST'
    else:
        role = services.role.get(db, id=user.role_id)
        role = role.name
    token_payload = {
        'id': user.id,
        'role': role,
    }
    access_token = create_access_token(
        token_payload, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type='bearer')


def encrypt_telegram_token(token):
    key = bytes(settings.TELEGRAM_TOKEN_ENCRYPTION_KEY, "utf-8")
    cipher = Fernet(key)
    return str(cipher.encrypt(bytes(token, "utf-8")))


def decrypt_telegram_token(token):
    key = bytes(settings.TELEGRAM_TOKEN_ENCRYPTION_KEY, "utf-8")
    cipher = Fernet(key)
    return str(cipher.decrypt(bytes(token, "utf-8")))

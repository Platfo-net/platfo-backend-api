from typing import Optional

from app.core.security import get_password_hash, verify_password
from app.services.base import BaseServices
from app.constants.role import Role
from sqlalchemy.orm import Session
from pydantic.types import UUID4
from app import models, schemas, services


class UserServices(
    BaseServices
    [
        models.User,
        schemas.UserCreate,
        schemas.UserUpdate
    ]
):
    def get_by_email(
        self, db: Session, *, email: str
    ) -> Optional[models.User]:
        return db.query(self.model).filter(models.User.email == email).first()

    def register(
        self,
        db: Session,
        *,
        obj_in: schemas.UserRegister
    ) -> models.User:

        user_role = services.role.get_by_name(db, name=Role.USER["name"])

        db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role_id=user_role.id,
            is_active=True
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.UserCreate,
    ) -> models.User:
        user_db_obj = models.User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            phone_number=obj_in.phone_number,
            is_active=obj_in.is_active,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role_id=obj_in.role_id
        )
        db.add(user_db_obj)
        db.commit()
        db.refresh(user_db_obj)
        return user_db_obj

    def change_password(
        self,
        db: Session,
        *,
        user_id: UUID4,
        new_password: str
    ):
        db_user = db.query(models.User).filter(
            models.User.id == user_id).first()
        db_user.hashed_password = get_password_hash(new_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> Optional[models.User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user) -> bool:
        return user.is_active

    def change_status(
        self, db: Session, *, id: UUID4
    ) -> Optional[models.User]:
        user = db.query(models.User).filter(models.User.id == id).first()
        user.is_active = not user.is_active
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get(self, db: Session, id: UUID4) -> Optional[models.User]:
        user = db.query(models.User).filter(models.User.id == id).first()
        return user


user = UserServices(models.User)

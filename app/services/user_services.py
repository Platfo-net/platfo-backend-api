from typing import Optional
from app.core.security import get_password_hash, verify_password
from app.services.base import BaseServices
from app.constants.role import Role
from sqlalchemy.orm import Session
from app import models, schemas, services


class UserServices(BaseServices[models.User, schemas.UserCreate, schemas.UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[models.User]:
        user = db.query(self.model).filter(self.model.email == email).first()
        return user

    def register(self, db: Session, *, obj_in: schemas.UserRegister) -> models.User:

        user_role = services.role.get_by_name(db, name=Role.USER["name"])

        db_obj = models.User(
            hashed_password=get_password_hash(obj_in.password),
            role_id=user_role.id,
            phone_number=obj_in.phone_number,
            phone_country_code=obj_in.phone_country_code,
            email=obj_in.email,
            is_email_verified=False,
            is_active=False,
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
            phone_country_code=obj_in.phone_country_code,
            is_email_verified=obj_in.is_email_verified,
            is_active=obj_in.is_active,
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            role_id=obj_in.role_id,
        )
        db.add(user_db_obj)
        db.commit()
        db.refresh(user_db_obj)
        return user_db_obj

    def change_password(
            self, db: Session, *, db_user: models.User, password: str
    ):
        db_user.hashed_password = get_password_hash(password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def authenticate_by_email(
            self, db: Session, *, email: str, password: str
    ) -> Optional[models.User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def authenticate_by_phone_number(
            self,
            db: Session,
            *,
            phone_number: str,
            phone_country_code: str,
            password: str
    ):
        user = self.get_by_phone_number(
            db,
            phone_number=phone_number,
            phone_country_code=phone_country_code
        )
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def activate(self, db: Session, *, user: models.User) -> Optional[models.User]:
        user.is_active = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_email(self, db: Session, *, user: models.User):
        user.is_email_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_phone_number(self, db: Session, *, phone_number: str, phone_country_code: str):
        return db.query(self.model).filter(
            self.model.phone_number == phone_number,
            self.model.phone_country_code == phone_country_code
        ).first()


user = UserServices(models.User)

from app import services, schemas
from sqlalchemy.orm import Session

from app.core.config import settings
from app.constants.role import Role
import pytest


def test_duplicate_user_creation_fail(db: Session):
    with pytest.raises(Exception):
        user_test_email = "test_duplicate@test.com"
        user_test_password = "test@123"
        role = services.role.get_by_name(db, name=Role.USER["name"])
        user_in = schemas.UserCreate(
            email=user_test_email, password=user_test_password, role_id=role.id
        )
        services.user.create(db, obj_in=user_in)

        services.user.create(db, obj_in=user_in)
    db.rollback()


def test_not_existed_user_login_fail(db: Session):
    wrong_user_email = "wrong@user.com"
    wrong_user_password = "wrong@123"

    user = services.user.authenticate(
        db, email=wrong_user_email, password=wrong_user_password
    )
    assert user is None


def test_existed_user_login_with_wrong_credential_fail(db: Session):
    wrong_user_password = "wrong@123"

    user = services.user.authenticate(
        db, email=settings.FIRST_USER_EMAIL, password=wrong_user_password
    )
    assert user is None

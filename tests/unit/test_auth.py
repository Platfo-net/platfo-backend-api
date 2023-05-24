import random
import string
import pytest
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.constants.role import Role
from app.core.security import create_token

sample_secure_password = "TestSecurePassword@123455"


def sample_email():
    return "".join(
        random.choice(f"{string.ascii_letters}") for _ in range(15)
    ) + "@example.com"


def sample_phone_number():
    return "".join(
        random.choice(f"{string.digits}") for _ in range(11)
    )


@pytest.fixture(scope="function")
def sample_user(db: Session):
    role_user = services.role.get_by_name(db, name=Role.USER["name"])
    user_in = schemas.UserCreate(
        phone_number="9123456780",
        phone_country_code="98",
        is_active=True,
        first_name="sample",
        last_name="sample pour",
        password=sample_secure_password,
        role_id=role_user.id,
        is_email_verified=True,
        email="sample@example.com"
    )
    user = services.user.create(db, obj_in=user_in)
    yield user
    services.user.remove(db, id=user.id)


@pytest.fixture(scope="function")
def sample_inactive_user(db: Session):
    role_user = services.role.get_by_name(db, name=Role.USER["name"])
    user_in = schemas.UserCreate(
        phone_number="9123456781",
        phone_country_code="98",
        is_active=False,
        first_name="sample inactive",
        last_name="sample pour inactive",
        password=sample_secure_password,
        role_id=role_user.id,
        is_email_verified=False,
        email="sample_inactive@example.com"
    )
    user = services.user.create(db, obj_in=user_in)
    yield user
    services.user.remove(db, id=user.id)


def test_create_access_token(db: Session, sample_user: models.User):
    token = create_token(db, user=sample_user)
    assert token.access_token is not None

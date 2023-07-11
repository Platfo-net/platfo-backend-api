from sqlalchemy.orm import Session

from app import models, schemas, services
from app.constants.role import Role
from tests.unit.fixtures import (sample_email, sample_phone_number,
                                 sample_secure_password)

from .fixtures import sample_inactive_user, sample_user  # noqa


def test_create_user(db: Session, sample_user: models.User): # noqa
    assert isinstance(sample_user, models.User)
    assert isinstance(sample_user.role, models.Role)
    assert sample_user.role.name == Role.USER['name']
    assert sample_user.is_active
    assert sample_user.is_email_verified


def test_activate_user(db: Session, sample_inactive_user: models.User): # noqa
    user = services.user.activate(db, user=sample_inactive_user)
    assert user.is_active


def test_verify_user_email(db: Session, sample_inactive_user: models.User): # noqa
    user = services.user.verify_email(db, user=sample_inactive_user)
    assert user.is_email_verified


def test_authenticate_user_by_email(db: Session, sample_user: models.User): # noqa
    user = services.user.authenticate_by_email(
        db,
        email=sample_user.email,
        password=sample_secure_password,
    )
    assert user is not None
    assert isinstance(user, models.User)


def test_authenticate_user_by_phone_number(db: Session, sample_user: models.User): # noqa
    user = services.user.authenticate_by_phone_number(
        db,
        phone_number=sample_user.phone_number,
        phone_country_code=sample_user.phone_country_code,
        password=sample_secure_password,
    )
    assert user is not None
    assert isinstance(user, models.User)


def test_get_user_by_email(db: Session, sample_user: models.User): # noqa
    user = services.user.get_by_email(db, email=sample_user.email)
    assert isinstance(user, models.User)
    assert user == sample_user


def test_get_user_by_phone_number(db: Session, sample_user: models.User): # noqa

    user = services.user.get_by_phone_number(
        db,
        phone_number=sample_user.phone_number,
        phone_country_code=sample_user.phone_country_code,
    )
    assert isinstance(user, models.User)
    assert user == sample_user


def test_get_user_by_id(db: Session, sample_user: models.User): # noqa
    user = services.user.get(db, id=sample_user.id)
    assert isinstance(user, models.User)
    assert user == sample_user


def test_get_user_by_uuid(db: Session, sample_user: models.User): # noqa
    user = services.user.get_by_uuid(db, uuid=sample_user.uuid)
    assert isinstance(user, models.User)
    assert user == sample_user


def test_register_user_by_email(db: Session): # noqa
    user_in = schemas.user.UserRegister(
        email=sample_email(),
        password=sample_secure_password,
        phone_number=sample_phone_number(),
        phone_country_code='98',
    )
    user = services.user.register(db, obj_in=user_in)
    assert isinstance(user, models.User)
    new_user = services.user.get(db, id=user.id)
    assert isinstance(new_user, models.User)

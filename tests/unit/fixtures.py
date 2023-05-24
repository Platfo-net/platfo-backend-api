
import random
import string

import pytest
from sqlalchemy.orm import Session

from app import schemas, services
from app.constants.role import Role

sample_secure_password = 'TestSecurePassword@123455'


def sample_email():
    return ''.join(
        random.choice(f'{string.ascii_letters}') for _ in range(15)
    ) + '@example.com'


def sample_phone_number():
    return ''.join(
        random.choice(f'{string.digits}') for _ in range(11)
    )


@pytest.fixture
def sample_user(db: Session):
    role_user = services.role.get_by_name(db, name=Role.USER['name'])
    user_in = schemas.UserCreate(
        phone_number='9123456780',
        phone_country_code='98',
        is_active=True,
        first_name='sample',
        last_name='sample pour',
        password=sample_secure_password,
        role_id=role_user.id,
        is_email_verified=True,
        email='sample@example.com'
    )
    user = services.user.create(db, obj_in=user_in)
    yield user
    services.user.remove(db, id=user.id)


@pytest.fixture
def sample_inactive_user(db: Session):
    role_user = services.role.get_by_name(db, name=Role.USER['name'])
    user_in = schemas.UserCreate(
        phone_number='9123456781',
        phone_country_code='98',
        is_active=False,
        first_name='sample inactive',
        last_name='sample pour inactive',
        password=sample_secure_password,
        role_id=role_user.id,
        is_email_verified=False,
        email='sample_inactive@example.com'
    )
    user = services.user.create(db, obj_in=user_in)
    yield user
    services.user.remove(db, id=user.id)


@pytest.fixture
def sample_instagram_page(db: Session):
    role_user = services.role.get_by_name(db, name=Role.USER['name'])
    user_in = schemas.UserCreate(
        phone_number='9123456780',
        phone_country_code='98',
        is_active=True,
        first_name='sample',
        last_name='sample pour',
        password=sample_secure_password,
        role_id=role_user.id,
        is_email_verified=True,
        email='sample@example.com'
    )
    user = services.user.create(db, obj_in=user_in)

    page_in = schemas.InstagramPageCreate(
        biography='sample biography',
        facebook_page_id=123456789,
        instagram_page_id=123456789,
        username='sample_username',
        profile_picture_url='sample_profile_picture.facebook.com',
        facebook_user_long_lived_token='quwidsfsjdfsdjfs',
        facebook_user_id='123456789',
        name='sample_name',
        website='sample_website.com',
        ig_id='123456789',
        followers_count=1,
        follows_count=1,
        user_id=user.id,
    )
    page = services.instagram_page.create(db, obj_in=page_in)
    yield page

    services.user.remove(db, id=user.id)
    services.instagram_page.remove(db, id=page.id)

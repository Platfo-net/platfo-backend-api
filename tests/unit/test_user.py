from app import services, schemas
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from tests.utils.utils import random_email, random_lower_string
from app.constants.role import Role


def test_register_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserRegister(email=email, password=password)
    user = services.user.register(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserRegister(email=email, password=password)
    user = services.user.register(db, obj_in=user_in)
    authenticated_user = services.user.authenticate(
        db, email=email, password=password
    )
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = services.user.authenticate(db, email=email, password=password)
    assert user is None


# def test_check_if_user_is_active(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = services.user.create(db, obj_in=user_in)
#     is_active = services.user.is_active(user)
#     assert is_active is True


# def test_check_if_user_is_active_inactive(db: Session) -> None:
#     email = random_email()
#     password = random_lower_string()
#     user_in = UserCreate(email=email, password=password)
#     user = services.user.create(db, obj_in=user_in)
#     is_active = services.user.is_active(user)
#     assert is_active


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = schemas.UserRegister(email=username, password=password)
    user = services.user.register(db, obj_in=user_in)
    user_2 = services.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = schemas.UserRegister(email=email, password=password)
    user = services.user.register(db, obj_in=user_in)
    first_name = random_lower_string()
    user_in_update = schemas.UserUpdate(first_name=first_name)
    services.user.update(db, db_obj=user, obj_in=user_in_update)
    user_2 = services.user.get(db, id=user.id)
    assert user_2
    assert user.email == user_2.email
    assert first_name == user_2.first_name


def test_create_user(db: Session):

    role = services.role.get_by_name(db, name=Role.ADMIN["name"])
    email = random_email()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        email=email,
        password=password,
        role_id=role.id,
    )

    user = services.user.create(db, obj_in=user_in)

    assert user.email == email
    assert hasattr(user, "hashed_password")

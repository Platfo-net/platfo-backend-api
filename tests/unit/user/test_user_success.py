from app import services, schemas, models
from sqlalchemy.orm import Session

from app.core.config import settings
from app.constants.role import Role


def test_test_user_created_success(db: Session):
    """
    Test creation of a user
    Test that test user created automatically is exist or not
    """
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    assert isinstance(user, models.User)
    assert user.email == settings.FIRST_USER_EMAIL


def test_test_admin_created_success(db: Session):
    """
    Test creation of a user
    Test that test admin created automatically is exist or not
    """
    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    assert isinstance(user, models.User)
    assert user.email == settings.FIRST_ADMIN_EMAIL


def test_register_user_success(db: Session):
    """
    Test user register
    registered user should have user role automatically
    """
    USER_TEST_EMAIL = "test_register@gmail.com"
    USER_TEST_PASSWORD = "test@123"
    user_in = schemas.UserRegister(email=USER_TEST_EMAIL, password=USER_TEST_PASSWORD)
    user = services.user.register(db, obj_in=user_in)
    user_role = services.role.get_by_name(db, name=Role.USER["name"])
    assert isinstance(user, models.User)
    assert user.role_id == user_role.id
    assert user.email == USER_TEST_EMAIL


def test_authenticate_user_success(db: Session):
    """
    Test authenticate user function
    that return User object if user exist and authenticate
    """
    admin = services.user.authenticate(
        db, email=settings.FIRST_ADMIN_EMAIL, password=settings.FIRST_ADMIN_PASSWORD
    )

    user = services.user.authenticate(
        db, email=settings.FIRST_USER_EMAIL, password=settings.FIRST_USER_PASSWORD
    )

    assert admin is not None
    assert user is not None
    assert isinstance(user, models.User)
    assert isinstance(admin, models.User)

    assert admin.email == settings.FIRST_ADMIN_EMAIL
    assert user.email == settings.FIRST_USER_EMAIL

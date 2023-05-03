from app import services, schemas
from app.constants.role import Role
from app.core.config import settings
from sqlalchemy.orm import Session


def init_db(db: Session) -> None:
    # Admin role
    admin_role = services.role.get_by_name(db, name=Role.ADMIN["name"])
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN["name"],
            description=Role.ADMIN["description"],
            persian_name=Role.ADMIN["persian_name"],
        )
        services.role.create(db, obj_in=admin_role_in)

    user_role = services.role.get_by_name(db, name=Role.USER["name"])
    if not user_role:
        user_role_in = schemas.RoleCreate(
            name=Role.USER["name"],
            description=Role.USER["description"],
            persian_name=Role.USER["persian_name"],
        )
        services.role.create(db, obj_in=user_role_in)

    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.ADMIN["name"])
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN_EMAIL,
            is_active=True,
            phone_number=settings.FIRST_ADMIN_PHONE_NUMBER,
            phone_country_code=settings.FIRST_ADMIN_PHONE_COUNTRY_CODE,
            is_email_verified=True,
            password=settings.FIRST_ADMIN_PASSWORD,
            role_id=role.id,
        )
        services.user.create(
            db,
            obj_in=user_in,
        )
    ramzinex_user = services.user.get_by_email(db, email="ramzinex@gmail.com")
    if not ramzinex_user:
        role = services.role.get_by_name(db, name=Role.USER["name"])
        user_in = schemas.UserCreate(
            email="ramzinex@gmail.com",
            is_active=True,
            phone_number="98",
            phone_country_code="9912345678",
            is_email_verified=True,
            password="Ramzinex@123",
            role_id=role.id,
        )
        services.user.create(
            db,
            obj_in=user_in,
        )


def init_test_db(db: Session) -> None:
    # Admin role
    admin_role = services.role.get_by_name(db, name=Role.ADMIN["name"])
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN["name"],
            description=Role.ADMIN["description"],
            persian_name=Role.ADMIN["persian_name"],
        )
        services.role.create(db, obj_in=admin_role_in)
    # User role
    user_role = services.role.get_by_name(db, name=Role.USER["name"])
    if not user_role:
        user_role_in = schemas.RoleCreate(
            name=Role.USER["name"],
            description=Role.USER["description"],
            persian_name=Role.USER["persian_name"],
        )
        services.role.create(db, obj_in=user_role_in)
    # Admin user
    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.ADMIN["name"])
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
            role_id=role.id,
        )
        services.user.create(
            db,
            obj_in=user_in,
        )
    # User user
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.USER["name"])
        user_in = schemas.UserCreate(
            email=settings.FIRST_USER_EMAIL,
            password=settings.FIRST_USER_PASSWORD,
            role_id=role.id,
        )
        services.user.create(db, obj_in=user_in)

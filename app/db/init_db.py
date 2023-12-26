from sqlalchemy.orm import Session

from app import schemas, services
from app.constants.payment_method import PaymentMethod
from app.constants.role import Role
from app.core.config import settings


def init_roles(db: Session) -> None:
    admin_role = services.role.get_by_name(db, name=Role.ADMIN['name'])
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN['name'],
            description=Role.ADMIN['description'],
            persian_name=Role.ADMIN['persian_name'],
        )
        services.role.create(db, obj_in=admin_role_in)

    user_role = services.role.get_by_name(db, name=Role.USER['name'])
    if not user_role:
        user_role_in = schemas.RoleCreate(
            name=Role.USER['name'],
            description=Role.USER['description'],
            persian_name=Role.USER['persian_name'],
        )
        services.role.create(db, obj_in=user_role_in)

    developer_role = services.role.get_by_name(db, name=Role.DEVELOPER['name'])
    if not developer_role:
        developer_role_in = schemas.RoleCreate(
            name=Role.DEVELOPER['name'],
            description=Role.DEVELOPER['description'],
            persian_name=Role.DEVELOPER['persian_name'],
        )
        services.role.create(db, obj_in=developer_role_in)


def init_users(db: Session) -> None:
    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.ADMIN['name'])
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
    developer = services.user.get_by_email(db, email=settings.FIRST_DEVELOPER_EMAIL)
    if not developer:
        d_role = services.role.get_by_name(db, name=Role.DEVELOPER['name'])
        developer_in = schemas.UserCreate(
            email=settings.FIRST_DEVELOPER_EMAIL,
            is_active=True,
            phone_number=settings.FIRST_DEVELOPER_PHONE_NUMBER,
            phone_country_code=settings.FIRST_DEVELOPER_PHONE_COUNTRY_CODE,
            is_email_verified=True,
            password=settings.FIRST_DEVELOPER_PASSWORD,
            role_id=d_role.id,
        )
        services.user.create(
            db,
            obj_in=developer_in,
        )


def init_payment_methods(db: Session):
    card_transfer = services.shop.payment_method.get_by_title(
        db, title=PaymentMethod.CARD_TRANSFER["title"])
    if not card_transfer:
        services.shop.payment_method.create(db, obj_in=schemas.shop.PaymentMethodCreate(
            title=PaymentMethod.CARD_TRANSFER["title"],
            description=PaymentMethod.CARD_TRANSFER["description"],
            information_fields=PaymentMethod.CARD_TRANSFER["information_fields"],
            payment_fields=PaymentMethod.CARD_TRANSFER["payment_fields"],
        ))

    on_spot = services.shop.payment_method.get_by_title(
        db, title=PaymentMethod.ON_SPOT["title"])
    if not on_spot:
        services.shop.payment_method.create(db, obj_in=schemas.shop.PaymentMethodCreate(
            title=PaymentMethod.ON_SPOT["title"],
            description=PaymentMethod.ON_SPOT["description"],
            information_fields=PaymentMethod.ON_SPOT["information_fields"],
            payment_fields=PaymentMethod.ON_SPOT["payment_fields"],
        ))
        
    zarrin_pal = services.shop.payment_method.get_by_title(
        db, title=PaymentMethod.ZARRIN_PAL["title"])
    if not zarrin_pal:
        services.shop.payment_method.create(db, obj_in=schemas.shop.PaymentMethodCreate(
            title=PaymentMethod.ZARRIN_PAL["title"],
            description=PaymentMethod.ZARRIN_PAL["description"],
            information_fields=PaymentMethod.ZARRIN_PAL["information_fields"],
            payment_fields=PaymentMethod.ZARRIN_PAL["payment_fields"],
        ))


def init_db(db: Session) -> None:
    init_roles(db)
    init_users(db)
    init_payment_methods(db)
    # asyncio.run(support_bot.set_support_bot_webhook())


def init_test_db(db: Session) -> None:
    # Admin role
    admin_role = services.role.get_by_name(db, name=Role.ADMIN['name'])
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN['name'],
            description=Role.ADMIN['description'],
            persian_name=Role.ADMIN['persian_name'],
        )
        services.role.create(db, obj_in=admin_role_in)
    # User role
    user_role = services.role.get_by_name(db, name=Role.USER['name'])
    if not user_role:
        user_role_in = schemas.RoleCreate(
            name=Role.USER['name'],
            description=Role.USER['description'],
            persian_name=Role.USER['persian_name'],
        )
        services.role.create(db, obj_in=user_role_in)
    # Admin user
    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.ADMIN['name'])
        user_in = schemas.UserCreate(
            phone_number=settings.FIRST_ADMIN_PHONE_NUMBER,
            phone_country_code=settings.FIRST_ADMIN_PHONE_COUNTRY_CODE,
            password=settings.FIRST_ADMIN_PASSWORD,
            role_id=role.id,
        )
        services.user.create(
            db,
            obj_in=user_in,
        )

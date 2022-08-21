from app import services, schemas
from app.constants.role import Role
from app.constants.trigger import Trigger
from app.core.config import settings
from sqlalchemy.orm import Session


def init_db(db: Session) -> None:

    # Admin role
    admin_role = services.role.get_by_name(
        db, name=Role.ADMIN["name"]
    )
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN["name"],
            description=Role.ADMIN["description"],
            persian_name=Role.ADMIN["persian_name"]
        )
        services.role.create(db, obj_in=admin_role_in)

    user_role = services.role.get_by_name(
        db, name=Role.USER["name"]
    )
    if not user_role:
        user_role_in = schemas.RoleCreate(
            name=Role.USER["name"],
            description=Role.USER["description"],
            persian_name=Role.USER["persian_name"]
        )
        services.role.create(db, obj_in=user_role_in)

    user = services.user.get_by_email(db, email=settings.FIRST_ADMIN_EMAIL)
    if not user:
        role = services.role.get_by_name(db, name=Role.ADMIN["name"])
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN_EMAIL,
            password=settings.FIRST_ADMIN_PASSWORD,
            role_id=role.id,
        )
        user = services.user.create(
            db,
            obj_in=user_in,
        )

    # creating triggers

    message_trigger = services.trigger.get_by_name(
        db, name=Trigger.Message["name"])

    if not message_trigger:
        services.trigger.create(
            db, obj_in=schemas.TriggerCreate(
                name=Trigger.Message["name"],
                persian_name=Trigger.Message["persian_name"],
                platform=Trigger.Message["platform"]
            )
        )

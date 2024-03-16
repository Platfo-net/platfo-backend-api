import uuid

from sqlalchemy.orm import Session

from app import schemas, services
from app.constants.application import Application
from app.constants.trigger import Trigger
from app.core.config import settings


def create_connection(db: Session, test_account_id):
    connection_in = schemas.ConnectionCreate(
        name='test',
        application_name=Application.BOT_BUILDER,
        description='test',
        account_id=test_account_id,
        details=[
            {'chatflow_id': str(uuid.uuid4()), 'trigger': Trigger.Message['name']}
        ],
    )

    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    return services.connection.create(db, obj_in=connection_in, user_id=user.id)


def create_chatflow(db: Session, user):
    chatflow_in = schemas.bot_builder.ChatflowCreate(
        name='test_chatflow', is_active=True
    )

    return services.bot_builder.chatflow.create(
        db=db, obj_in=chatflow_in, user_id=user.id
    )


def create_user(db: Session):
    return services.user.get_by_email(db=db, email=settings.FIRST_USER_EMAIL)

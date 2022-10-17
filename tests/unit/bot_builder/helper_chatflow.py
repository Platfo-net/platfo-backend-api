from sqlalchemy.orm import Session

from app import services, schemas
from app.core.config import settings


def helper_chatflow(db: Session):
    chatflow_in = schemas.bot_builder.ChatflowCreate(
        name='test_chatflow',
        is_active=True
    )
    user = services.user.get_by_email(
                db=db,
                email=settings.FIRST_USER_EMAIL
    )
    return services.bot_builder \
        .chatflow.create(db=db, obj_in=chatflow_in, user_id=user.id)

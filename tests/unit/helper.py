import uuid

from sqlalchemy.orm import Session

from app import services, schemas
from app.constants.application import Application
from app.constants.trigger import Trigger
from app.core.config import settings


def create_connection(db: Session, test_account_id):
    connection_in = schemas.ConnectionCreate(
        name="test",
        application_name=Application.BOT_BUILDER["name"],
        description="test",
        account_id=test_account_id,
        details=[
            {
                "chatflow_id": str(uuid.uuid4()),
                "trigger": Trigger.Message["name"]
            }
        ]
    )

    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    return services.connection.create(
        db, obj_in=connection_in, user_id=user.id)


def create_chatflow(db: Session, user):
    chatflow_in = schemas.bot_builder.ChatflowCreate(
        name='test_chatflow',
        is_active=True
    )

    return services.bot_builder \
        .chatflow.create(db=db, obj_in=chatflow_in, user_id=user.id)


def create_category(db: Session):
    category_in = schemas.academy.CategoryCreate(
        title='cat1',
        parent_id=None
    )

    return services.academy.category.create(db=db, obj_in=category_in)


def create_label(db: Session):
    label_in = schemas.academy.LabelCreate(
        name='label1'
    )

    return services.academy.label.create(db=db, obj_in=label_in)


def create_content(db: Session, user_id):
    content_in = schemas.academy.ContentCreate(
            title="مقاله تستی",
            blocks=[  # noqa
                {
                    "id": "1234567",
                    "type": "paragraph",
                    "data": {
                        "text": "hello this is a sample text",
                    },
                }
            ],
            caption="this is a good article",
            is_published=True,
            version="2.24.3",
            time="1663757930863",
            slug="مقاله-تستی",
            cover_image="test_image",
            categories=[  # noqa
                {
                    "category_id": "418f667a-6f82-4611-a764-ad7ea12100fc"
                }
            ],
            labels=[  # noqa
                {
                    "label_id": "df4939b0-f4c6-4b8b-8085-a7b4030898ab"
                }
            ]
    )

    return services.academy.content.create(db=db, obj_in=content_in, user_id=user_id)


def create_user(db: Session):
    return services.user.get_by_email(
        db=db,
        email=settings.FIRST_USER_EMAIL
    )

from sqlalchemy.orm import Session

from app import services, models
from tests.unit.bot_builder.helper_chatflow import helper_chatflow


def test_create_chatflow(db: Session):
    chatflow = helper_chatflow(db=db)

    assert isinstance(chatflow, models.bot_builder.Chatflow)
    assert chatflow.is_active == 1


def test_get_chatflow(db: Session):
    chatflow = helper_chatflow(db=db)
    chatflow_obj = services.bot_builder.chatflow.get(
        db=db,
        id=chatflow.id,
        user_id=chatflow.user.id
    )
    assert chatflow_obj.id == chatflow.id
    assert chatflow_obj.user_id == chatflow.user.id


def test_delete_chatflow(db: Session):
    chatflow = helper_chatflow(db=db)
    services.bot_builder.chatflow.delete_chatflow(db=db, id=chatflow.id)
    chatflow_after_delete = services.bot_builder.chatflow.get(
        db=db,
        id=chatflow.id,
        user_id=chatflow.user.id
    )
    assert isinstance(chatflow, models.bot_builder.Chatflow)
    assert chatflow_after_delete is None


def test_get_user_chatflows(db: Session):
    chatflows = []
    for _ in range(3):
        chatflows.append(helper_chatflow(db=db))

    chatflow_list = services.bot_builder.chatflow.get_multi(
            db, user_id=chatflows[0].user_id
    )

    assert chatflow_list[1].user_id == chatflows[0].user_id

from sqlalchemy.orm import Session

from app import services, models
from tests.unit import helper


def test_get_user_chatflows(db: Session):
    user = helper.create_user(db=db)
    chatflow = helper.create_chatflow(db=db, user=user)
    chatflow_list = services.bot_builder.chatflow.get_multi(
        db, user_id=chatflow.user_id
    )

    assert isinstance(chatflow, models.bot_builder.Chatflow)
    assert len(chatflow_list) == 2
    assert type(chatflow_list[1]) == list
    assert chatflow_list[1][0].user_id == chatflow.user_id


def test_create_chatflow(db: Session):
    user = helper.create_user(db=db)
    chatflow = helper.create_chatflow(db=db, user=user)

    assert isinstance(chatflow, models.bot_builder.Chatflow)


def test_get_chatflow(db: Session):
    user = helper.create_user(db=db)
    chatflow = helper.create_chatflow(db=db, user=user)
    chatflow_obj = services.bot_builder.chatflow.get(
        db=db, id=chatflow.id, user_id=chatflow.user.id
    )
    assert chatflow_obj.id == chatflow.id
    assert chatflow_obj.user_id == chatflow.user.id


def test_delete_chatflow(db: Session):
    user = helper.create_user(db=db)
    chatflow = helper.create_chatflow(db=db, user=user)
    services.bot_builder.chatflow.delete_chatflow(db=db, id=chatflow.id)
    chatflow_after_delete = services.bot_builder.chatflow.get(
        db=db, id=chatflow.id, user_id=chatflow.user.id
    )
    assert chatflow_after_delete is None

from sqlalchemy.orm import Session

from app import services, models

# helper_chatflow ro bokon helper va 
# be soorate zir import kon va azash estefade kon
# from tests.unit.bot_builder import helper
# helper.create_chatflow
# jahaye dige ham age in karo kardi dorostesh kon

# test delete ham dorost nist. chechesh kon
from tests.unit.bot_builder.helper_chatflow import helper_chatflow


def test_get_user_chatflows(db: Session):
    chatflow = helper_chatflow(db=db)
    chatflow_list = services.bot_builder.chatflow.get_multi(
            db, user_id=chatflow.user_id
    )

    assert isinstance(chatflow, models.bot_builder.Chatflow)
    assert len(chatflow_list) == 1
    assert type(chatflow_list) == list
    assert chatflow_list[0].user_id == chatflow.user_id


def test_create_chatflow(db: Session):
    chatflow = helper_chatflow(db=db)

    assert isinstance(chatflow, models.bot_builder.Chatflow)


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
    assert chatflow_after_delete is None



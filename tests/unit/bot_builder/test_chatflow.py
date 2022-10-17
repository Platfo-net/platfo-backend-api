from sqlalchemy.orm import Session

from app import services, models

# helper_chatflow ro bokon helper va 
# be soorate zir import kon va azash estefade kon
# from tests.unit.bot_builder import helper
# helper.create_chatflow
# jahaye dige ham age in karo kardi dorostesh kon

# test delete ham dorost nist. chechesh kon
from tests.unit.bot_builder.helper_chatflow import helper_chatflow


def test_create_chatflow(db: Session):
    # chon chatflow fielde mohemmi nadare 
    # fgt test kon ke instance dorosti dare ya na
    # man dorostesh kardam
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


# teste delete dorost kar nemikone 

# def test_delete_chatflow(db: Session):
#     chatflow = helper_chatflow(db=db)
#     services.bot_builder.chatflow.delete_chatflow(db=db, id=chatflow.id)
#     chatflow_after_delete = services.bot_builder.chatflow.get(
#         db=db,
#         id=chatflow.id,
#         user_id=chatflow.user.id
#     )
#     assert chatflow_after_delete is None


def test_get_user_chatflows(db: Session):
    # vaseye in fgt yedoone ham besazi kafie
    # test kon bebin list barmigardoone ya na
    # check kon toole list 1 bashe
    # check kon avvalish instance dorost hastesh ya na
    chatflows = []
    for _ in range(3):
        chatflows.append(helper_chatflow(db=db))

    chatflow_list = services.bot_builder.chatflow.get_multi(
            db, user_id=chatflows[0].user_id
    )

    assert chatflow_list[1].user_id == chatflows[0].user_id

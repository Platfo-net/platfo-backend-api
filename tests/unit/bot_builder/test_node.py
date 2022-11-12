import uuid

from sqlalchemy.orm import Session

from app import schemas, services, models
from app.core.utils import widget_mapper
from tests.unit import helper


def test_create_node(db: Session):
    user = helper.create_user(db=db)
    chatflow = helper.create_chatflow(db=db, user=user)
    node_in = schemas.bot_builder.NodeCreate(
        chatflow_id=chatflow.id,
        title='test_node',
        is_head=True,
        quick_replies=[{"id": uuid.uuid4(), "text": "you want it or not?"}]  # noqa
    )
    node = services.bot_builder.node.create(db=db, obj_in=node_in)

    assert isinstance(node, models.bot_builder.Node)
    assert node.chatflow_id == chatflow.id


def test_widget_mapper_menu(db: Session):
    data = {
        "type": "MENU",
        "question": "ccc",
        "choices": [
            {
                "value": "bec3ee2b-9846-4459-96bd-9c60c3fa8ccf",
                "label": "cccvv",
                "action": {
                    "type": "GOTO",
                    "data": ""
                }
            }
        ],
        "quickReplies": []
    }
    node_id = uuid.uuid4()
    widget, quick_replies = widget_mapper(data=data, node_id=node_id)

    assert type(widget) == dict
    assert type(quick_replies) == list
    assert widget['widget_type'] == 'MENU'
    assert widget['id'] == str(node_id)


def test_widget_mapper_text(db: Session):
    data = {
        "type": "TEXT",
        "value": "vbc",
        "quickReplies": [
        ]
    }
    node_id = uuid.uuid4()
    widget, quick_replies = widget_mapper(data=data, node_id=node_id)

    assert type(widget) == dict
    assert type(quick_replies) == list
    assert widget['widget_type'] == 'TEXT'
    assert widget['id'] == str(node_id)


# def test_create_full_node(db: Session):
#     chatflow = helper(db=db)
#     node_in = schemas.bot_builder.FullNodeCreate(
#         chatflow_id=chatflow.id,
#         title='test_node',
#         is_head=True,
#         widget_type=random_widget_type(),
#         widget={"message": "hello"},
#         quick_replies=[{"id": uuid.uuid4(), "text": "you want it or not?"}]  # noqa
#     )
#     node = services.bot_builder.node.create(db=db, obj_in=node_in)
#
#     assert isinstance(node, models.bot_builder.Node)
#     assert node.chatflow_id == chatflow.id

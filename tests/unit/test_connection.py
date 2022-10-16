from app import services, schemas, models
from sqlalchemy.orm import Session
import uuid
from app.constants.application import Application
from app.constants.trigger import Trigger

from tests.unit import helper


def test_create_connection_success(db: Session):
    test_account_id = uuid.uuid4()
    connection = helper.create_connection(db, test_account_id)

    assert isinstance(connection, models.Connection)
    assert len(connection.details) == 1
    assert connection.application_name == Application.BOT_BUILDER["name"]


def test_update_connection_success(db: Session):
    test_account_id = uuid.uuid4()
    db_connection = helper.create_connection(db, test_account_id)
    test_new_account_id = uuid.uuid4()
    chatflow_id = str(uuid.uuid4())
    connection_in = schemas.ConnectionUpdate(
        name=db_connection.name,
        description="test_updated",
        application_name=Application.BOT_BUILDER["name"],
        account_id=test_new_account_id,
        details=[
            {
                "chatflow_id": chatflow_id,
                "trigger": Trigger.Message["name"]
            }
        ]
    )

    connection = services.connection.update(
        db,
        user_id=db_connection.user_id,
        db_obj=db_connection,
        obj_in=connection_in
    )
    assert isinstance(connection, models.Connection)
    assert connection.account_id == test_new_account_id
    assert connection.description == "test_updated"
    assert connection.application_name == Application.BOT_BUILDER["name"]
    assert len(connection.details) == 1
    assert connection.details[0]["chatflow_id"] == chatflow_id
    assert connection.details[0]["trigger"] == Trigger.Message["name"]


def test_delete_connection_success(db: Session):
    test_account_id = uuid.uuid4()
    connection = helper.create_connection(db, test_account_id)
    services.connection.remove(db, id=connection.id)

    db_connection = services.connection.get(db, connection.id)

    assert db_connection is None


def test_get_connection_by_account_id_and_app_name(db: Session):
    test_account_id = uuid.uuid4()
    helper.create_connection(db, test_account_id)
    existed_connection = services.connection\
        .get_by_application_name_and_account_id(
            db,
            account_id=str(test_account_id),
            application_name=Application.BOT_BUILDER["name"])

    not_existed_connection = services.connection\
        .get_by_application_name_and_account_id(
            db,
            account_id=str(uuid.uuid4()),
            application_name=Application.BOT_BUILDER["name"]
        )
    assert not_existed_connection is None
    assert existed_connection.application_name == \
        Application.BOT_BUILDER["name"]
    assert existed_connection.account_id == test_account_id
    assert len(existed_connection.details) == 1

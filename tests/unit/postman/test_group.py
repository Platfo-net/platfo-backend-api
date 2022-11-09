from sqlalchemy.orm import Session
from app import services, schemas, models
from app.core.config import settings
from tests.unit.postman import helper


def test_create_group(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="1")
    group = helper.create_group(db, user.id, account.facebook_page_id)

    assert isinstance(group, models.postman.Group)
    assert group.user_id == user.id
    assert group.facebook_page_id == "1"


def test_update_group(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="2")
    db_obj = helper.create_group(db, user.id, account.facebook_page_id)

    obj_in = schemas.postman.GroupUpdate(
        name="test_group_updated",
        description="test_group_description_updated",
    )

    group = services.postman.group.update(
            db,
            user_id=user.id,
            db_obj=db_obj,
            obj_in=obj_in
    )

    assert isinstance(group, models.postman.Group)
    assert group.name == "test_group_updated"
    assert group.description == "test_group_description_updated"
    assert group.user_id == db_obj.user_id


def test_delete_content(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="2")
    group = helper.create_group(
        db,
        user_id=user.id,
        facebook_page_id=account.facebook_page_id
    )

    services.postman.group.remove(db, id=group.id, user_id=user.id)

    group_after_delete = services.postman.group.get(db=db, id=group.id)

    assert group_after_delete is None


def test_get_groups(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="4")
    group = helper.create_group(
        db=db,
        user_id=user.id,
        facebook_page_id=account.facebook_page_id
    )

    groups_list = services.postman.group.get_multi(
        db=db,
        facebook_page_id=group.facebook_page_id,
        user_id=user.id
    )

    assert isinstance(group, models.postman.Group)
    assert len(groups_list) >= 1
    assert type(groups_list[1]) == list
    assert groups_list[1][0].id == group.id
    assert groups_list[1][0].name == group.name

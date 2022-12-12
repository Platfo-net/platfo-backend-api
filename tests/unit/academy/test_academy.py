from sqlalchemy.orm import Session

from app import services, models, schemas
from tests.unit import helper


def test_get_categories(db: Session):
    category = helper.create_category(db=db)
    categories_list = services.academy.category.get_multi(db=db)

    assert isinstance(category, models.academy.Category)
    assert len(categories_list) >= 1
    assert type(categories_list[0]) == list
    assert categories_list[0][0].id == category.id


def test_create_category(db: Session):
    category = helper.create_category(db=db)

    assert isinstance(category, models.academy.Category)


def test_delete_category(db: Session):
    category = helper.create_category(db=db)
    services.academy.category.remove(db=db, id=category.id)
    category_after_delete = services.academy.category.get(db=db, id=category.id)

    assert category_after_delete is None


def test_get_labels(db: Session):
    label = helper.create_label(db=db)
    labels_list = services.academy.label.get_multi(db=db)

    assert isinstance(label, models.academy.Label)
    assert len(labels_list) >= 1
    assert type(labels_list[0]) == list
    assert labels_list[0][0].id == label.id


def test_create_label(db: Session):
    label = helper.create_label(db=db)

    assert isinstance(label, models.academy.Label)


def test_delete_label(db: Session):
    label = helper.create_label(db=db)
    services.academy.label.remove(db=db, id=label.id)
    label_after_delete = services.academy.label.get(db=db, id=label.id)

    assert label_after_delete is None


def test_create_content(db: Session):
    user = helper.create_user(db=db)
    content = helper.create_content(db=db, user_id=user.id)

    assert isinstance(content, models.academy.Content)
    assert content.user_id == user.id


def test_delete_content(db: Session):
    user = helper.create_user(db=db)
    content = helper.create_content(db, user_id=user.id)
    services.academy.content.remove(db, id=content.id)

    content_after_delete = services.academy.content.get(db=db, id=content.id)

    assert content_after_delete is None


def test_update_content(db: Session):
    user = helper.create_user(db=db)
    old_content = helper.create_content(db, user_id=user.id)
    content_in = schemas.academy.ContentUpdate(
        title="مقاله تستی آپدیت شده",
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
        cover_image="test_image_updated",
        categories=[{"category_id": "418f667a-6f82-4611-a764-ad7ea12100fb"}],  # noqa
        labels=[{"label_id": "df4939b0-f4c6-4b8b-8085-a7b4030898at"}],  # noqa
    )
    content = services.academy.content.update(
        db=db, user_id=old_content.user_id, db_obj=old_content, obj_in=content_in
    )
    assert isinstance(content, models.academy.Content)
    assert content.user_id == old_content.user_id
    assert content.title == "مقاله تستی آپدیت شده"
    assert len(content.blocks) == 1

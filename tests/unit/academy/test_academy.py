from sqlalchemy.orm import Session

from app import services, models
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
    content = helper.create_content(db=db, user=user)

    assert isinstance(content, models.academy.Content)
    assert content.user_id == user.id

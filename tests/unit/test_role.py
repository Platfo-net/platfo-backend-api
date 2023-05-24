import pytest
from sqlalchemy.orm import Session

from app import models, schemas, services


@pytest.fixture
def sample_role(db: Session):
    role_in = schemas.RoleCreate(
        name="SampleRole", description="Sample",
    )
    role = services.role.create(db, obj_in=role_in)
    yield role
    services.role.remove(db, id=role.id)


def test_create_role_successfully(db: Session, sample_role):
    assert isinstance(sample_role, models.Role)


def test_update_role_successfully(db: Session, sample_role: models.Role):
    new_role = services.role.update(db, db_obj=sample_role, obj_in=schemas.RoleUpdate(
        name="NewSampleRole", description="New Sample"
    ))
    assert isinstance(new_role, models.Role)

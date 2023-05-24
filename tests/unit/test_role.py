from sqlalchemy.orm import Session

from app import models, schemas, services


def test_create_role_successfully(db: Session):
    role_in = schemas.RoleCreate(name="TEST", description="TEST")
    role = services.role.create(db, obj_in=role_in)

    assert isinstance(role, models.Role)
    assert role.name == "TEST"

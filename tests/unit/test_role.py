from app import services, schemas, models
from sqlalchemy.orm import Session


def test_create_role_successfully(db: Session):
    role_in = schemas.RoleCreate(
        name="TEST",
        description="TEST"
    )
    role = services.role.create(db, obj_in=role_in)

    assert isinstance(role, models.Role)
    assert role.name == "TEST"

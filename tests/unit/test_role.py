from app import services, schemas
from sqlalchemy.orm import Session
from tests.utils.utils import random_lower_string


def test_create_role(db: Session) -> None:
    role_name = random_lower_string()
    role_in = schemas.RoleCreate(
        name=role_name,
        description=random_lower_string(),
        persian_name=random_lower_string()

    )
    role = services.role.create(db, obj_in=role_in)

    role_in_db = services.role.get(db, role.id)

    assert role
    assert role.id == role_in_db.id
    assert role_in_db.name == role_name

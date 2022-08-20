from typing import Optional

from app.services.base import BaseServices
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate
from sqlalchemy.orm import Session


class RoleServices(BaseServices[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        return db.query(self.model).filter(Role.name == name).first()


role = RoleServices(Role)

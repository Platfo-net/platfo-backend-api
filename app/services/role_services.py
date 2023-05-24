from typing import Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.services.base import BaseServices


class RoleServices(BaseServices[models.Role, schemas.RoleCreate, schemas.RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Role]:
        return db.query(self.model).filter(self.model.name == name).first()


role = RoleServices(models.Role)

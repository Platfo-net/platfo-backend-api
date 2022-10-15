from typing import Optional

from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas


class RoleServices(BaseServices[models.Role, schemas.RoleCreate, schemas.RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[models.Role]:
        return db.query(self.model).filter(self.model.name == name).first()


role = RoleServices(models.Role)

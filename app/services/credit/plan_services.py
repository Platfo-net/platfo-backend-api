from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from app import models


class PlanServices:
    def __init__(self, model):
        self.model: models.credit.Plan = model

    def get(self, db: Session, id: int) -> Optional[models.credit.Plan]:
        return (
            db.query(self.model)
            .join(self.model.features)
            .filter(self.model.id == id)
            .first()
        )

    def get_by_uuid(self, db: Session, uuid: UUID4) -> Optional[models.credit.Plan]:
        return (
            db.query(self.model)
            .join(self.model.features)
            .filter(self.model.uuid == uuid)
            .first()
        )

    def get_multi(
        self, db: Session, *, currency: str, module: str = None
    ) -> List[models.credit.Plan]:
        if not module:
            return db.query(self.model).all()
        return (
            db.query(self.model)
            .filter(
                self.model.module == module,
                self.model.currency == currency,
            )
            .all()
        )


plan = PlanServices(models.credit.Plan)

from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session


class TriggerServices(
        BaseServices[
            schemas.Trigger,
            schemas.TriggerCreate,
            schemas.TriggerUpdate
        ]):
    def get_by_name(self, db: Session, name: str) -> schemas.Trigger:
        return db.query(self.model).filter(self.model.name == name).first()


trigger = TriggerServices(models.Trigger)
